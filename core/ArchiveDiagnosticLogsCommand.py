import os
from shutil import copytree, ignore_patterns, rmtree
from tempfile import mkdtemp
import tarfile
import traceback

from StcPython import StcPython


def validate(FileName):
    return ''


def run(FileName):
    try:
        stc = StcPython()
        log_dir = stc.perform('GetSystemPaths').get('SessionDataPath', '')
        stc.perform('SaveEquipmentInfoCommand')
        stc.perform('GetEquipmentLogsCommand',
                    EquipmentList='project1', TimestampFileNames=False)
        stc.perform('SaveToTccCommand',
                    FileName=os.path.join(log_dir, 'config.tcc'))
        _archive(stc, FileName, log_dir)

    except Exception:
        stc.log('ERROR',
                'error: unhandled exception:\n' + traceback.format_exc())
        return False

    return True


def reset():
    return True


def _archive(stc, file_name, log_dir):
    base_tmp_dir = mkdtemp()
    try:
        tmp_dir = os.path.join(base_tmp_dir, 'stc_logs')
        stc.log('INFO', 'copy %s to %s' % (log_dir, tmp_dir))
        try:
            copytree(log_dir, tmp_dir, ignore=ignore_patterns('*sandbox', '*.db*'))
        except Exception as err:
            stc.log('WARN', 'Some files may not have been copied\n\t%s' % err)

        out_filename = os.path.join(log_dir, file_name)
        stc.log('INFO', 'gzip %s to %s' % (tmp_dir, out_filename))
        with tarfile.open(out_filename, 'w:gz') as tar:
            tar.add(tmp_dir, arcname=os.path.basename(tmp_dir))
    finally:
        stc.log('INFO', 'remove temp directory %s' % base_tmp_dir)
        rmtree(base_tmp_dir, ignore_errors=True)
        stc.perform('AddRemoteFileCommand', FileName=out_filename, Category='LOG')
