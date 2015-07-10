from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand

unsaved_attribute = None


# Set command attribute.
# If command handle is not available, the attribute is saved temporarily
# in unsaved_attribute,
# and can be retrieved later from this module
def set_attribute(att, value, command):
    global unsaved_attribute
    if command:
        command.Set(att, value)
    else:
        unsaved_attribute = value


def set_collection(att, values, command):
    global unsaved_attribute
    if command:
        command.SetCollection(att, values)
    else:
        unsaved_attribute = values


def exec_command(command, params):
    with AutoCommand('spirent.methodology.trafficcenter.' + command) as cmd:
        for k, v in params.iteritems():
            if type(v) is list:
                cmd.SetCollection(k, v)
            else:
                cmd.Set(k, v)
        cmd.Execute()
    return cmd
