from StcIntPythonPL import *
import spirent.methodology.VerifyDynamicResultViewDataCommand as vdrvdCmd
import spirent.methodology.ExportDynamicResultViewDataCommand as exportCmd


def test_export_validate(stc):
    ctor = CScriptableCreator()
    assert 'No dynamic result view provided.' == exportCmd.validate(False, False, [],
                                                                    "GROUP_1", "")
    project = CStcSystem.Instance().GetObject('project')
    drv = ctor.Create("DynamicResultView", project)
    drv.Set('Name', 'TestDrv1')
    drvs = []
    drvs.append(drv.Get('Name'))
    assert '' == exportCmd.validate(False, False, drvs, "GROUP_1", "")
    drv2 = ctor.Create("DynamicResultView", project)
    drv2.Set('Name', 'ALLUPPER2')
    drvs.append('AllUpper2')
    assert '' == exportCmd.validate(False, False, drvs, "GROUP_1", "")
    drvs.append('NoDrv3')
    expectedStr = 'Unable to find dynamic result views from name:NoDrv3'
    assert expectedStr == exportCmd.validate(False, False, drvs, "GROUP_1", "")


def test_verifydrvdata_validate(stc):
    pass
    ctor = CScriptableCreator()
    project = CStcSystem.Instance().GetObject('project')
    drv = ctor.Create("DynamicResultView", project)
    drv.Set('Name', 'ValidateDrv2')
    assert '' == vdrvdCmd.validate(False, 'ValidateDrv2', 0, 0, 0, 0, "GROUP_1", "", "", "")
    assert '' == vdrvdCmd.validate(False, 'VaLIDATEdRV2', 0, 0, 0, 0, "GROUP_1", "", "", "")
    expectedStr = 'Unable to find Dynamic result view from name:MyDrv'
    assert expectedStr == vdrvdCmd.validate(False, 'MyDrv', 0, 0, 0, 0, "SUMMARY", "", "", "")
