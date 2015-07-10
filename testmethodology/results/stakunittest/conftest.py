import pytest
from StcIntPythonPL import *
import os


@pytest.fixture
def stc(request):
    utm = UnitTestManager.Instance()
    utm.Init('base core stak')
    mm = CStcSystem.Instance().GetObject('StmMethodologyManager')
    if mm is None:
        ctor = CScriptableCreator()
        mm = ctor.Create("StmMethodologyManager")
    # delete files
    dir = CTestResultSettingExt.GetResultDbBaseDirectory()
    if os.path.exists(dir):
        filelist = [f for f in os.listdir(dir) if f.endswith(".json")]
        for f in filelist:
            os.remove(os.path.join(dir, f))
    return utm


@pytest.fixture
def resource_cleanup(request):
    def fin():
        mm = CStcSystem.Instance().GetObject('StmMethodologyManager')
        if mm is not None:
            tr = mm.GetObject('StmTestResult')
            if tr is not None:
                tr.MarkDelete()
    request.addfinalizer(fin)
    return None
