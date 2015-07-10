from StcIntPythonPL import *
from results.ResultInterface import ResultInterface


def validate():
    return ""


def run():
    ResultInterface.create_test()
    ResultInterface.start_test()
    return True


def reset():
    return True
