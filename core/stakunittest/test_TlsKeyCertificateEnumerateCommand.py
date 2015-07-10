from StcIntPythonPL import *
from spirent.core.TlsKeyCertificateEnumerateCommand \
    import *


def SetupPort():
    system = CStcSystem.Instance()
    proj = system.GetObject('project')
    ctor = CScriptableCreator()
    port = ctor.Create('port', proj)
    return port


def test_validate(stc, resource_cleanup):
    port = SetupPort()
    assert validate([port.GetObjectHandle()]) == ''


def test_run(stc, resource_cleanup):
    port = SetupPort()
    # since offline should timeout
    assert not run([port.GetObjectHandle()])


def test_reset(stc):
    assert reset()