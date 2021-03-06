from StcIntPythonPL import CScriptableCreator


class AutoCommand(object):
    '''
    AutoCommand manages the lifetime of a Command.
    Use in conjuction with the with statement to create a Command,
    set its properties, and execute. On with
    statement completion, the Command will automatically get
    marked for deletion, thus avoiding any potential memory leaks.
    Example:
    with AutoCommand('CreatorCommand') as cmd:
        cmd.Set('CreateClassId', 'streamblock')
        cmd.Set('CreateCount', 10)
        cmd.Execute()
    Note: You can still dereference the Command until the next apply.
    But, be careful that you don't call apply, then try to dereference
    the Command!
    '''

    def __init__(self, class_name):
        '''
        class_name - The class name of the command to create.
        '''
        self.__class_name = class_name
        self.__cmd = None

    def __enter__(self):
        ctor = CScriptableCreator()
        self.__cmd = ctor.CreateCommand(self.__class_name)
        return self.__cmd

    def __exit__(self, type, value, traceback):
        if self.__cmd and not self.__cmd.IsDeleted():
            self.__cmd.MarkDelete()


class AutoScriptable(object):
    '''
    AutoScriptable manages the lifetime of a Scriptable.
    Use in conjuction with the with statement to create a Scriptable.
    On with statement completion, the Scriptable will automatically get
    marked for deletion, thus avoiding any potential memory leaks.
    Example:
    with AutoScriptable('streamblock', project) as streamblock:
        // Do something with streamblock
    This is mostly useful as an alternative to cleaning up in the
    tearDown function of a unit test.
    Be careful that you don't call apply, then try to dereference
    the Scriptable!
    '''

    def __init__(self, class_name, parent=None):
        '''
        class_name - The class name of the Scriptable to create.
        parent - The parent.
        '''
        self.__class_name = class_name
        self.__parent = parent
        self.__scriptable = None

    def __enter__(self):
        ctor = CScriptableCreator()
        self.__scriptable = ctor.Create(self.__class_name, self.__parent)
        return self.__scriptable

    def __exit__(self, type, value, traceback):
        if self.__scriptable and not self.__scriptable.IsDeleted():
            self.__scriptable.MarkDelete()
