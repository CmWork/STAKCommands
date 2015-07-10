from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand


def test_run():
    CObjectRefStore.Put('spirent.core.one', 1)
    CObjectRefStore.Put('spirent.core.two', 2)
    CObjectRefStore.Put('spirent.core.three', 3)
    with AutoCommand('spirent.core.ReleaseObjectReferenceCommand') as cmd:
        cmd.Set('Key', 'spirent.core.two')
        cmd.Execute()
    assert CObjectRefStore.Exists('spirent.core.one')
    assert not CObjectRefStore.Exists('spirent.core.two')
    assert CObjectRefStore.Exists('spirent.core.three')
    with AutoCommand('spirent.core.ReleaseObjectReferenceCommand') as cmd:
        cmd.Execute()
    assert not CObjectRefStore.Exists('spirent.core.one')
    assert not CObjectRefStore.Exists('spirent.core.three')
