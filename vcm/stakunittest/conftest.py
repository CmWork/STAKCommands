import pytest
from StcIntPythonPL import (UnitTestManager)


@pytest.fixture
def stc(request):
    utm = UnitTestManager.Instance()
    utm.Init('base core stak')
    return utm
