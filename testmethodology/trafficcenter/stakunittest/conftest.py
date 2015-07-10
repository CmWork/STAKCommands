import pytest
from StcIntPythonPL import *
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def stc(request):
    utm = UnitTestManager.Instance()
    utm.Init('base core l2l3 stak arp dhcpv4 dhcpv6')
    return utm


@pytest.fixture(scope="session")
def clean_up(request, stc):
    ctor = CScriptableCreator()
    cmd = ctor.CreateCommand("ResetConfigCommand")

    cmd.Set("Config", CStcSystem.Instance().GetObjectHandle())
    cmd.Execute()
