from StcIntPythonPL import *
from spirent.core.TlsKeyCertificateDeleteCommand \
    import *


def SetupPorts():
    system = CStcSystem.Instance()
    proj = system.GetObject('project')
    ctor = CScriptableCreator()
    port1 = ctor.Create('port', proj)
    port2 = ctor.Create('port', proj)
    physChassisMgr = system.GetObject("physicalchassismanager")
    physChassis = ctor.Create("physicalchassis", physChassisMgr)
    physTm1 = ctor.Create("physicaltestmodule", physChassis)
    physTm2 = ctor.Create("physicaltestmodule", physChassis)
    physPg1 = ctor.Create("physicalportgroup", physTm1)
    physPg2 = ctor.Create("physicalportgroup", physTm2)
    physPort1 = ctor.Create("physicalport", physPg1)
    physPort2 = ctor.Create("physicalport", physPg2)
    port1.AddObject(physPort1, RelationType.ReverseDir("PhysicalLogical"))
    port2.AddObject(physPort2, RelationType.ReverseDir("PhysicalLogical"))
    physTm1.Set("Name", "TestMod1")
    physTm2.Set("Name", "TestMod2")
    retParameters = dict()
    retParameters['proj'] = proj
    retParameters['port'] = [port1, port2]
    return retParameters


def SetupPortsSinglePortGroup():
    system = CStcSystem.Instance()
    proj = system.GetObject('project')
    ctor = CScriptableCreator()
    port1 = ctor.Create('port', proj)
    port2 = ctor.Create('port', proj)
    physChassisMgr = system.GetObject("physicalchassismanager")
    physChassis = ctor.Create("physicalchassis", physChassisMgr)
    physTm1 = ctor.Create("physicaltestmodule", physChassis)
    physPg1 = ctor.Create("physicalportgroup", physTm1)
    physPort1 = ctor.Create("physicalport", physPg1)
    physPort2 = ctor.Create("physicalport", physPg1)
    port1.AddObject(physPort1, RelationType.ReverseDir("PhysicalLogical"))
    port2.AddObject(physPort2, RelationType.ReverseDir("PhysicalLogical"))
    physTm1.Set("Name", "TestMod1")
    retParameters = dict()
    retParameters['proj'] = proj
    retParameters['port'] = [port1, port2]
    return retParameters


def test_validate(stc, resource_cleanup):
    config = SetupPorts()
    fileList = ['test.txt']
    assert len(validate([], fileList, 'PRIVATE_KEY')) > 0
    assert validate([config['proj'].GetObjectHandle()], 'test.txt', 'CERTIFICATE') == ''
    assert validate([config['port'][0].GetObjectHandle()], 'test.txt', 'CA_CERTIFICATE') == ''


def test_SetPortGroupHandles(stc, resource_cleanup):
    config = SetupPorts()
    cmd = TlsKeyCertificateDeleteCommandHelper()
    cmd._portGroupSet.clear()
    cmd._isUnitTest = True
    cmd.SetPortGroupHandles([config['port'][0], config['port'][1]])
    assert len(cmd._portGroupSet) == 2

    cmd = TlsKeyCertificateDeleteCommandHelper()
    cmd._portGroupSet.clear()
    cmd._isUnitTest = True
    cmd.SetPortGroupHandles([config['port'][0]])
    assert len(cmd._portGroupSet) == 1

    cmd = TlsKeyCertificateDeleteCommandHelper()
    cmd._objHandleList = []
    cmd._portGroupSet.clear()
    cmd._isUnitTest = True
    cmd.SetPortGroupHandles([config['port'][0]])
    cmd.SetPortGroupHandles([config['port'][0]])
    assert len(cmd._portGroupSet) == 1

    cmd = TlsKeyCertificateDeleteCommandHelper()
    cmd._portGroupSet.clear()
    cmd._isUnitTest = False
    cmd.SetPortGroupHandles([config['port'][0]])
    assert len(cmd._portGroupSet) == 0


def test_SetPortGroupHandlesSinglePortGroup(stc, resource_cleanup):
    config = SetupPortsSinglePortGroup()
    cmd = TlsKeyCertificateDeleteCommandHelper()
    cmd._portGroupSet = set()
    cmd._isUnitTest = True
    cmd.SetPortGroupHandles([config['port'][0], config['port'][1]])

    assert not len(cmd._portGroupSet) == 2
    assert len(cmd._portGroupSet) == 1


def test_reset(stc):
    assert reset()
