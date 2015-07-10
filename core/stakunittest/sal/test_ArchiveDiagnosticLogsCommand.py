import os
import tarfile
from StcIntPythonPL import CStcSystem, UnitTestManager
utm = UnitTestManager.Instance()
utm.Init('base core')
from spirent.core.ArchiveDiagnosticLogsCommand import *

TEST_FILE = 'test_diagnostic_logs.tgz'


def test_validate():
    assert validate(TEST_FILE) == ''


def test_run(stc):
    assert run(TEST_FILE)
    out_filename = os.path.join(CStcSystem.GetLogOutputPath(), TEST_FILE)
    assert os.path.exists(out_filename)
    assert tarfile.is_tarfile(out_filename)


def test_reset():
    assert reset()
