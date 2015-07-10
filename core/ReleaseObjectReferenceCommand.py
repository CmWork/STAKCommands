from StcIntPythonPL import *


def validate(Key):
    return ''


def run(Key):
    if not Key:
        CObjectRefStore.Reset()
    elif CObjectRefStore.Exists(Key):
        CObjectRefStore.Release(Key)
    return True


def reset():
    return True
