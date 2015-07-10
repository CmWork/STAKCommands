from StcIntPythonPL import *
from ..utils.CommandUtils import *
import pytest


def clear():
    project = CStcSystem.Instance().GetObject('project')
    for tp in project.GetObjects('TrafficProfile'):
        tp.MarkDelete()


@pytest.fixture
def cleanup(request, stc):
    clear()

    def fin():
        clear()
    request.addfinalizer(fin)


def test_set_attribute(stc):
    ctor = CScriptableCreator()
    Cmd = ctor.CreateCommand('GetFieldOffsetCommand')
    set_attribute("Offset", 1, Cmd)
    assert Cmd.Get("Offset") == 1
