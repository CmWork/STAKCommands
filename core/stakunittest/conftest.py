import pytest
from StcIntPythonPL import CStcSystem, UnitTestManager


@pytest.fixture
def stc(request):
    utm = UnitTestManager.Instance()
    utm.Init('base core stak datacenter')
    return utm


@pytest.fixture
def resource_cleanup(request):
    def fin():
        project = CStcSystem.Instance().GetObject('project')
        for port in project.GetObjects('Port'):
            port.MarkDelete()
        physChassisMgr = CStcSystem.Instance().GetObject('physicalchassismanager')
        for chassis in physChassisMgr.GetObjects('physicalchassis'):
            chassis.MarkDelete()
    request.addfinalizer(fin)
    return None
