"""
Downloads STC feature license file from a license server

"""
import glob
import os
import platform
import re
import shutil
import subprocess
import time
import traceback
# pexpect not supported on windows
if not platform.system().startswith('Windows'):
    import pexpect

from StcIntPythonPL import (PLLogger, CStcSystem)

CMD_NAME = 'spirent.core.DownloadFeatureLicenseCommand'


def validate(Server, TargetFilename):
    """Validate the input parameters for this STAK command.

    Arguments:
    Server - License server IP or hostname
    TargetFilename - File path where license file will be downloaded

    Return:
    Empty string if OK, error message string if error with input.

    """
    # Server must not be empty
    if not Server:
        return 'Specify a license server IP or hostname'

    # TargetFilename must end with .lic extension
    base, ext = os.path.splitext(TargetFilename)
    if ext != '.lic':
        return 'TargetFilename must have a .lic file extension'

    # ensure that the local directory paths to target file exist so create the directory
    # if it doesn't already exist
    try:
        target_file = os.path.abspath(os.path.expanduser(TargetFilename))
        target_dir = os.path.dirname(target_file)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
    except Exception as e:
        return 'Unable to create directory %s\n%s' % (target_dir, str(e))

    return ''


def run(Server, TargetFilename):
    """Run the DownloadFeatureLicenseCommand STAK command.

    Arguments:
    Server - License server IP or hostname
    TargetFilename - File path where license file will be downloaded

    """
    logger = get_logger()
    try:
        # get the absolute path to target file
        target_file = os.path.abspath(os.path.expanduser(TargetFilename))

        # remove existing target file
        if os.path.exists(target_file):
            try:
                os.remove(target_file)
            except OSError:
                logger.LogError('Unable to remove existing license file: ' + target_file)
                return False

        if platform.system().startswith('Windows'):
            # create download directory for licenses
            session_data_path = CStcSystem.Instance().GetApplicationSessionDataPath()
            download_dir = os.path.join(session_data_path, "licenses")
            logger.LogDebug('download dir: ' + download_dir)
            if not os.path.exists(download_dir):
                logger.LogDebug('create download dir')
                os.makedirs(download_dir)
            else:
                # clean out all license files from download directory
                purge_license_files(download_dir)

            # copy all feature licenses from samba share on the server
            feature_files_path = os.path.abspath(r'\\' + Server + '/feature-licenses/*.lic')
            logger.LogDebug('feature files: {}'.format(feature_files_path))
            feature_files = []
            max_attempts = 5
            for i in range(max_attempts):
                feature_files = glob.glob(feature_files_path)
                if feature_files:
                    break
                else:
                    logger.LogDebug('Attempt #{0}: '
                                    'Unable to find license files on server.'.format(i + 1))
            # ensure we have something to copy
            if not feature_files:
                logger.LogError('No license files (.lic) found on server')
                ping_server(Server)
                return False
            # copy the files and place in the download directory
            for file in feature_files:
                if os.path.isfile(file):
                    logger.LogDebug('downloading %s' % str(file))
                    shutil.copy(file, download_dir)

            # there may be multiple feature license files in the samba share
            # so we need to concat all the files into a single license file
            read_files = glob.glob(os.path.join(download_dir, '*.lic'))
            if not read_files:
                logger.LogError('No license files (.lic) copied from server')
                ping_server(Server)
                return False
            with open(target_file, "wb") as outfile:
                for f in read_files:
                    with open(f, "rb") as infile:
                        outfile.write(infile.read())

            logger.LogDebug('Removing download directory')
            shutil.rmtree(download_dir, ignore_errors=True)
        else:
            # on *nix we may not have root access to mount the samba share so we will use expect
            # and scp to download the feature licenses from the tmp directory.  we're grabbing it
            # from here instead of the samba share to avoid multi-access issues.  the license
            # file in /tmp is already concatenated from the *.lic files in the samba share.  the
            # license server does this on startup.
            lic_path = "/tmp/features.lic"
            scp_cmd = ('scp -o GSSAPIAuthentication=no '
                       '-o StrictHostKeyChecking=no '
                       '-o ConnectTimeout=30 '
                       'stc@{0}:{1} "{2}"').format(Server, lic_path, target_file)
            log_file = get_tmp_log_file()
            # augment the environment scp runs in by removing STC paths from LD_LIBRARY_PATH
            # to avoid conflicts
            scp_env = sanitize_ld_lib_path([CStcSystem.Instance().GetApplicationCommonDataPath()])
            if 'LD_LIBRARY_PATH' in scp_env:
                logger.LogDebug('LD_LIBRARY_PATH: ' + scp_env['LD_LIBRARY_PATH'])
            try:
                child = pexpect.spawn(scp_cmd, logfile=log_file, env=scp_env, echo=False)
            except pexpect.ExceptionPexpect as e:
                logger.LogError('Unable to spawn scp command: %s\n%s' % (scp_cmd, str(e)))
                # Ensure the log file is closed
                if log_file is not None:
                    log_file.close()
                    # Remove the log file
                    if os.path.exists(log_file.name):
                        os.remove(log_file.name)
                return False

            try:
                # loop allows us to process multiple license files
                index = -1
                while True:
                    index = child.expect(['(?i)password',
                                          'Connection refused',
                                          'Connection timed out',
                                          '100%',
                                          pexpect.EOF,
                                          pexpect.TIMEOUT])
                    if index == 0:
                        child.sendline('spirent')
                        continue
                    elif index == 3:
                        continue
                    elif index == 1:
                        logger.LogDebug('Connection refused')
                        ping_server(Server)
                    elif index == 2:
                        logger.LogDebug('Connection timed out')
                        ping_server(Server)
                    elif index == 4:
                        logger.LogDebug('EOF received')
                    elif index == 5:
                        logger.LogDebug('timeout exceeded')
                        ping_server(Server)
                    break
            except pexpect.ExceptionPexpect as e:
                logger.LogError('pexpect exception: ' + str(e))
                return False
            except Exception as e:
                logger.LogError(str(e))
                return False
            finally:
                logger.LogDebug('index: %s' % index)
                # Log the debug output
                if log_file is not None:
                    log_file.seek(0)
                    for line in log_file:
                        # redact the password from the log
                        line = re.sub('(?i)password: [a-z]+', 'password: ***', line.rstrip())
                        logger.LogDebug('  %s' % line)
                # Ensure the log file is closed
                if log_file is not None:
                    log_file.close()
                    # Remove the log file
                    if os.path.exists(log_file.name):
                        os.remove(log_file.name)
                child.close()

    except RuntimeError as e:
        logger.LogError('Runtime exception: ' + str(e))
        ping_server(Server)
        return False
    except IOError as e:
        logger.LogError('I/O exception: ' + str(e))
        ping_server(Server)
        return False
    except:
        logger.LogError('Unhandled exception:\n' + traceback.format_exc())
        ping_server(Server)
        return False

    if not os.path.isfile(target_file):
        logger.LogError('Error downloading feature license(s) from server')
        return False

    logger.LogInfo('Feature license download was successful')
    return True


def reset():
    """True means this command can be reset and re-run."""
    return True


def get_logger():
    """Get the logger for this command"""
    return PLLogger.GetLogger(CMD_NAME)


def purge_license_files(dir):
    for f in os.listdir(dir):
        if f.endswith('.lic'):
            os.remove(os.path.join(dir, f))


def get_tmp_log_file():
    """Creates a temporary file for logging purposes.

    The function is used to create a temporary file to hold the log output
    generated when executing pexpect. The caller is expected to close the
    file in order to remove the file when it is no longer needed.

    Return: The function returns a file object. If an error occurs,
         a None value will be returned.
    """
    try:
        # Get a log file to write the output to
        ts = time.strftime("%Y%m%d-%H%M%S")
        filename = '/tmp/scp_log_' + ts + '_' + str(os.getpid()) + '.log'
        return open(filename, 'w+')
    except Exception, error:
        get_logger().LogError('Unable to create a temporary log file to capture'
                              ' the scp output: %s' % str(error))
    return None


def sanitize_ld_lib_path(removal_list):
    """Removes all occurrences of specified paths from LD_LIBRARY_PATH

    Arguments:
    removal_list - list of paths to remove

    """
    env = os.environ.copy()
    if 'LD_LIBRARY_PATH' in env:
        ld_lib_path = env['LD_LIBRARY_PATH'].split(os.pathsep)
        clean = []
        for path in ld_lib_path:
            if path in removal_list:
                continue
            clean.append(path)
        env['LD_LIBRARY_PATH'] = os.pathsep.join(clean)
    return env


def ping_server(server):
    """Pings the server

    Arguments:
    server - server to ping

    """
    if platform.system().startswith('Windows'):
        count_option = '-n'
    else:
        count_option = '-c'
    args = ['ping', count_option, '3', server]
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutdata, stderrdata = p.communicate()
    get_logger().LogDebug(stdoutdata)
    if p.returncode != 0:
        raise RuntimeError('Unable to ping ' + server + '.  ' + stderrdata)
