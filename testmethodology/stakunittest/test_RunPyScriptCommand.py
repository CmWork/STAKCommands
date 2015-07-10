from StcIntPythonPL import *
from mock import MagicMock
import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'STAKCommands', 'spirent', 'methodology'))
import RunPyScriptCommand
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as mmutils


def test_chart_script(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()
    pkg = "spirent.methodology"

    tags = project.GetObject('Tags')
    tagA = ctor.Create("tag", tags)
    tagA.Set("Name", "tagA")

    cmd = ctor.Create(pkg + ".RunPyScriptCommand", sequencer)
    RunPyScriptCommand.get_this_cmd = MagicMock(return_value=cmd)

    cmd2 = ctor.Create(pkg + ".ExportDbChartCommand", sequencer)
    cmd2.AddObject(tagA, RelationType("UserTag"))

    script_folder = mmutils.get_scripts_home_dir()
    filename = os.path.join(script_folder, "unit_test_file_chart.py")
    try:
        if not os.path.exists(script_folder):
            os.makedirs(script_folder)
        with open(filename, "w") as f:
            f.write(unit_test_file_chart())
        RunPyScriptCommand.run("unit_test_file_chart", "run", "tagA", {'a': {'b': [1, 2]}})
        assert cmd2.Get("CustomModifier") == "{'a': {'b': [1, 2]}}"
    finally:
        remove_files(filename)
    return


def remove_files(filename):
    if os.path.isfile(filename):
        os.remove(filename)
    if os.path.isfile(filename+'c'):
        os.remove(filename+'c')
    return


def unit_test_file_chart():
    return '''
from StcIntPythonPL import *
def run(TagName, TaggedObjects, Params):
    TaggedObjects[0].Set("CustomModifier", str(Params))
    return ""
'''


def test_simple_script(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()
    pkg = "spirent.methodology"

    tags = project.GetObject('Tags')
    tagA = ctor.Create("tag", tags)
    tagA.Set("Name", "tagA")

    cmd = ctor.Create(pkg + ".RunPyScriptCommand", sequencer)
    RunPyScriptCommand.get_this_cmd = MagicMock(return_value=cmd)

    cmd2 = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    cmd2.AddObject(tagA, RelationType("UserTag"))

    script_folder = mmutils.get_scripts_home_dir()
    filename = os.path.join(script_folder, "unit_test_file_simple.py")
    try:
        if not os.path.exists(script_folder):
            os.makedirs(script_folder)
        with open(filename, "w") as f:
            f.write(unit_test_file_simple())
        RunPyScriptCommand.run("unit_test_file_simple", "run_set_copies", "tagA", {})
        assert cmd2.Get("CopiesPerParent") == 6
    finally:
        remove_files(filename)
    return


def unit_test_file_simple():
    return '''
from StcIntPythonPL import *
def run_set_copies(TagName, TaggedObjects, Params):
    TaggedObjects[0].Set("CopiesPerParent", 6)
    return ""
'''


def test_param_a_to_script(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()
    pkg = "spirent.methodology"

    tags = project.GetObject('Tags')
    tagA = ctor.Create("tag", tags)
    tagA.Set("Name", "tagA")

    cmd = ctor.Create(pkg + ".RunPyScriptCommand", sequencer)
    RunPyScriptCommand.get_this_cmd = MagicMock(return_value=cmd)

    cmd2 = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    cmd2.AddObject(tagA, RelationType("UserTag"))

    script_folder = mmutils.get_scripts_home_dir()
    filename = os.path.join(script_folder, "unit_test_file_param_a_to_script.py")
    try:
        if not os.path.exists(script_folder):
            os.makedirs(script_folder)
        with open(filename, "w") as f:
            f.write(unit_test_file_param_a_to_script())
        RunPyScriptCommand.run("unit_test_file_param_a_to_script", "run", "tagA", {'a': 4})
        assert cmd2.Get("CopiesPerParent") == 4
    finally:
        remove_files(filename)
    return


def unit_test_file_param_a_to_script():
    return '''
from StcIntPythonPL import *
def run(TagName, TaggedObjects, Params):
    TaggedObjects[0].Set("CopiesPerParent", Params['a'])
    return ""
'''


def test_multi_tagged(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()
    pkg = "spirent.methodology"

    tags = project.GetObject('Tags')
    tagA = ctor.Create("tag", tags)
    tagA.Set("Name", "tagA")

    cmd = ctor.Create(pkg + ".RunPyScriptCommand", sequencer)
    RunPyScriptCommand.get_this_cmd = MagicMock(return_value=cmd)

    cmd2 = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    cmd2.AddObject(tagA, RelationType("UserTag"))

    cmd3 = ctor.Create(pkg + ".LoadTemplateCommand", sequencer)
    cmd3.AddObject(tagA, RelationType("UserTag"))

    script_folder = mmutils.get_scripts_home_dir()
    filename = os.path.join(script_folder, "unit_test_file_multi_tagged.py")
    try:
        if not os.path.exists(script_folder):
            os.makedirs(script_folder)
        with open(filename, "w") as f:
            f.write(unit_test_file_multi_tagged())
        RunPyScriptCommand.run("unit_test_file_multi_tagged", "run", "tagA", {'a': [4, 5]})
        assert cmd2.Get("CopiesPerParent") == 4
        assert cmd3.Get("CopiesPerParent") == 5
    finally:
        remove_files(filename)
    return


def unit_test_file_multi_tagged():
    return '''
from StcIntPythonPL import *
def run(TagName, TaggedObjects, Params):
    i = 0
    for to in TaggedObjects:
        to.Set("CopiesPerParent", Params['a'][i])
        i = i + 1
    return ""
'''


def hold_test_error_returned(stc):
    stc_sys = CStcSystem.Instance()
    project = stc_sys.GetObject('Project')
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()
    pkg = "spirent.methodology"

    tags = project.GetObject('Tags')
    tagA = ctor.Create("tag", tags)
    tagA.Set("Name", "tagA")

    cmd = ctor.Create(pkg + ".RunPyScriptCommand", sequencer)
    RunPyScriptCommand.get_this_cmd = MagicMock(return_value=cmd)

    script_folder = mmutils.get_scripts_home_dir()
    filename = os.path.join(script_folder, "unit_test_file_error_returned.py")
    try:
        if not os.path.exists(script_folder):
            os.makedirs(script_folder)
        with open(filename, "w") as f:
            f.write(unit_test_file_error_returned())
        rc = RunPyScriptCommand.run("unit_test_file_error_returned", "errorout", "tagA", {})
        assert rc is False
        assert cmd.Get("ErrorMsg") != ""
    finally:
        remove_files(filename)
    return


def unit_test_file_error_returned():
    return '''
from StcIntPythonPL import *
def errorout(TagName, TaggedObjects, Params):
    return "an error message"
'''


def test_validate_valid_file():
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()
    pkg = "spirent.methodology"

    cmd = ctor.Create(pkg + ".RunPyScriptCommand", sequencer)
    RunPyScriptCommand.get_this_cmd = MagicMock(return_value=cmd)

    script_folder = mmutils.get_scripts_home_dir()
    filename = os.path.join(script_folder, "unit_test_file_valid_script.py")
    try:
        if not os.path.exists(script_folder):
            os.makedirs(script_folder)
        with open(filename, "w") as f:
            f.write(unit_test_file_valid_script())
        err = RunPyScriptCommand.validate("unit_test_file_valid_script", "run", "tagA", "")
        assert err == ""
        err = RunPyScriptCommand.validate("unit_test_file_valid_script.py", "run", "tagA", "")
        assert err == ""
    finally:
        remove_files(filename)
    return


def unit_test_file_valid_script():
    return '''
from StcIntPythonPL import *
def run(TagName, TaggedObjects, Params):
    return ""
'''


def test_validate_missing_file():
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()
    pkg = "spirent.methodology"

    cmd = ctor.Create(pkg + ".RunPyScriptCommand", sequencer)
    RunPyScriptCommand.get_this_cmd = MagicMock(return_value=cmd)
    err = RunPyScriptCommand.validate("unit_test_file_missing_script", "run", "tagA", "")
    assert err != ""


def test_validate_missing_method():
    stc_sys = CStcSystem.Instance()
    sequencer = stc_sys.GetObject("Sequencer")
    ctor = CScriptableCreator()
    pkg = "spirent.methodology"

    cmd = ctor.Create(pkg + ".RunPyScriptCommand", sequencer)
    RunPyScriptCommand.get_this_cmd = MagicMock(return_value=cmd)

    script_folder = mmutils.get_scripts_home_dir()
    filename = os.path.join(script_folder, "unit_test_file_valid_script.py")
    try:
        if not os.path.exists(script_folder):
            os.makedirs(script_folder)
        with open(filename, "w") as f:
            f.write(unit_test_file_valid_script())
        err = RunPyScriptCommand.validate("unit_test_file_valid_script", "", "tagA", "")
        assert err != ""
    finally:
        remove_files(filename)
    return