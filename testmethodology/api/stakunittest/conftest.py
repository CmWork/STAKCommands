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
