import pytest
from StcIntPythonPL import *


@pytest.fixture
def stc(request):
    utm = UnitTestManager.Instance()
    utm.Init('base core l2l3 stak bfd bgp dhcpv4 dhcpv6 custom arp')

    def clean_up():
        ctor = CScriptableCreator()
        cmd = ctor.CreateCommand("ResetConfigCommand")
        cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
        cmd.Execute()

    request.addfinalizer(clean_up)
    return utm


@pytest.fixture
def meth_mgr(request):
    stc_sys = CStcSystem.Instance()
    m_mgr = stc_sys.GetObject('StmMethodologyManager')
    if m_mgr is None:
        ctor = CScriptableCreator()
        m_mgr = ctor.Create('StmMethodologyManager', stc_sys)

    def fin():
        mm = CStcSystem.Instance().GetObject('StmMethodologyManager')
        tr_list = mm.GetObjects('StmTestResult')
        if len(tr_list) > 0:
            for tr in tr_list:
                tr.MarkDelete()
    request.addfinalizer(fin)
    return None
