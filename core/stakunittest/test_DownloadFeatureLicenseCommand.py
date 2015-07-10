import platform
# temporarily disable on *nix until virtualenv can be set up for unit tests
if platform.system().startswith('Windows'):
    from spirent.core.DownloadFeatureLicenseCommand import *


    def test_validate():
        # skip this test on *nix since it may not have expect installed
        if platform.system().startswith('Windows'):
            assert validate('1.1.1.1', '/tmp/foo/bar.lic') == ''
            assert validate('1.1.1.1', 'foo:/bar/baz.lic').startswith('Unable to create directory')
        assert validate('', 'tmp/foo/bar.lic') == 'Specify a license server IP or hostname'
        assert validate('1.1.1.1', '/tmp/foo/bar.txt') == 'TargetFilename must have a .lic file extension'


    ''' Testing the run() method requires an actual license server.
    def test_run(stc):
        with pytest.raises(RuntimeError) as excinfo:
            run('1.1.1.1', '/tmp/foo/bar.lic')
        assert 'Unable to ping 1.1.1.1' in str(excinfo.value)
        # requires a live server
        # assert run('license.cal.ci.spirentcom.com', '/tmp/foo/bar.lic')
    '''

    def test_reset():
        assert reset()
