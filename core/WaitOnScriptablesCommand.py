from StcIntPythonPL import *


def getLogger():


    logger = PLLogger.GetLogger('spirent.core')
    return logger


class WaitOnScriptablesCommand:
    '''Abstract class to wait on Scriptable objects, similar to BLL class
        CWaitOnScriptablesCommmand
        FIXME: Rightnow added in spirent.switching.vxlan due to a bug in
        inheritence across different packages.
        Must be moved to spirent.core package
    '''


    def __init__(self, objHandleList, waitTime):
        self._objHandleList = objHandleList
        self._waitTime = waitTime
        self._objectList = []
        self._successful = []


    def FillObjectsList(self, objectHandleList):
        '''Virtual function to overide by derived class
           Derived class must fill the self._objectList with the appropriate
           objects to wait on using the passed objectHandleList
        '''
        raise Exception('FillObjectsList not implemented,'
                        'derived class should implement the FillObjectsList')


    def DoRun(self, waitProperty, waitState):
        ''' Function to wait on the objects filled by FillObjectsList using the
            waitProperty and waitState supplied.
            Returns true if wait is successful on all objects, false otherwise
        '''

        getLogger().LogDebug('At DoRun')
        if len(self._objectList) == 0:
            self.FillObjectsList(self._objHandleList)
        if len(self._objectList) == 0:
            getLogger().LogInfo('No objects to wait on')
            return True
        upFlag = 0
        currentTimeout = 0
        self._successful = []
        taskMgr = CTaskManager.Instance()
        while currentTimeout < self._waitTime and upFlag == 0:
            upFlag = 1
            for obj in self._objectList:
                propertyVal = obj.Get(waitProperty)
                if propertyVal != waitState:
                    upFlag = 0
                    break
                else:
                    self._successful.append(obj.GetObjectHandle())
            if upFlag == 0:
                taskMgr.CtmYield(1000)
                currentTimeout += 1
        if upFlag == 1:
            return True
        return False


    def GetSuccessfulObjects(self):
        '''Get the handle list for which the wait was successful.
           Call after DoRun completes
        '''
        return self._successful


    def GetUnsuccessfulObjects(self):
        '''Get the handle list for which the wait was unsuccessful
           Call after DoRun completes
        '''
        successSet = set(self._successful)
        waitHandleList = [obj.GetObjectHandle() for obj in self._objectList]
        return [handle for handle in waitHandleList
                if handle not in successSet]
