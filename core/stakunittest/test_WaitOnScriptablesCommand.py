from StcIntPythonPL import *
from spirent.core.WaitOnScriptablesCommand import *
import time


class Dummy(WaitOnScriptablesCommand):
    def FillObjectsList(self, objectHandleList):
        self._objectList = objectHandleList


def test_WaitOnScriptablesCommand(stc):
    proj = CStcSystem.Instance().GetObject('project')
    ctor = CScriptableCreator()
    port1 = ctor.Create('Port', proj)
    device1 = ctor.Create('EmulatedDevice', proj)
    port1.AddObject(device1, RelationType.ReverseDir('AffiliationPort'))
    vtepCfg1 = ctor.Create('VxlanVtepConfig', device1)
    vtepCfg1.Set('Active', True)

    port2 = ctor.Create('Port', proj)
    device2 = ctor.Create('EmulatedDevice', proj)
    port2.AddObject(device2, RelationType.ReverseDir('AffiliationPort'))
    vtepCfg2 = ctor.Create('VxlanVtepConfig', device2)
    vtepCfg2.Set('Active', True)

    # For convenience passing in objects not handles
    testCmd = Dummy([vtepCfg1, vtepCfg2], 10)
    assert testCmd._waitTime == 10
    assert len(testCmd._objectList) == 0
    assert len(testCmd._objHandleList) == 2
    assert testCmd.DoRun('State', 'STOPPED')

    successList = testCmd.GetSuccessfulObjects()
    assert len(successList) == 2
    unsuccessList = testCmd.GetUnsuccessfulObjects()
    assert len(unsuccessList) == 0

    successList = []
    unsuccessList = []
    # time in secs
    currTime = time.time()
    assert not testCmd.DoRun('State', 'STARTED')
    elapsedTime = time.time()
    assert (elapsedTime - currTime) >= 10.0
    successList = testCmd.GetSuccessfulObjects()
    assert len(successList) == 0
    unsuccessList = testCmd.GetUnsuccessfulObjects()
    assert len(unsuccessList) == 2
