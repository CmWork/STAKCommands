import pytest
from StcIntPythonPL import (CScriptableCreator, CStcSystem, UnitTestManager)


@pytest.fixture
def stc(request):
    utm = UnitTestManager.Instance()
    utm.Init('base core stak l2l3')

    def clean_up():
        ctor = CScriptableCreator()
        cmd = ctor.CreateCommand("ResetConfigCommand")
        cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        cmd.Execute()

    request.addfinalizer(clean_up)
    return utm
