from StcIntPythonPL import *


def validate(PollingInterval, ValueIdleTimeout, PropertyList,
             ResultParent, EnableCondition, TerminalValueList):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("Validate SetupSubscriptionCommand")

    # Validate PollingInterval
    if PollingInterval < 1:
        err = "PollingInterval must be at least 1 second"
        plLogger.LogError(err)
        raise RuntimeError(err)

    # Validate PropertyList
    if PropertyList is None or len(PropertyList) == 0:
        err = "PropertyList must contain at least one property: i.e. \"cfg.res.prop\""
        plLogger.LogError(err)
        raise RuntimeError(err)

    listThreeples = PropertyList.split(' ')
    numsProps = len(listThreeples)

    for threeple in listThreeples:
        if threeple.count('.') != 2:
            err = "Properties within the space-delimited PropertyList must" \
                  " be of the format:  ConfigType.ResultType.Property"
            plLogger.LogError(err)
            raise RuntimeError(err)

    # Validate ResultParent
    if ResultParent is None or len(ResultParent) == 0:
        err = "ResultParent must contain at least one parent object (Project, Port, Device)"
        plLogger.LogError(err)
        raise RuntimeError(err)

    # Validate TerminalValueList
    if EnableCondition is True:
        numTerminals = len(TerminalValueList)
        if numTerminals != numsProps:
            err = "TerminalValueList must contain the same numbers of items as PropertyList"
            plLogger.LogError(err)
            raise RuntimeError(err)

    return ''


def run(PollingInterval, ValueIdleTimeout, PropertyList,
        ResultParent, EnableCondition, TerminalValueList):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo("Run SetupSubscriptionCommand")

    project = CStcSystem.Instance().GetObject("project")
    projHnd = project.GetObjectHandle()
    ctor = CScriptableCreator()

    key = 'spirent.methodology.sampling'
    if not CObjectRefStore.Exists(key):
        empty_dict = {}
        CObjectRefStore.Put('spirent.methodology.sampling', empty_dict)
    sampDict = CObjectRefStore.Get(key)
    if 'Subscription' not in sampDict:
        sampDict['Subscription'] = []
    # Everything in python is by reference, so we can modify subList
    subList = sampDict['Subscription']

    listThreeples = PropertyList.split(' ')
    # Iterate through both lists simultaneously
    for threeple, terminal in map(None, listThreeples, TerminalValueList):

        if threeple is None:
            # TODO: error handling
            break

        # Was unsuccessful trying to reuse the same command object, hence repeated creation
        sub_cmd = ctor.CreateCommand("ResultsSubscribeCommand")
        if sub_cmd is None:
            # TODO: error handling
            plLogger.LogError("ERROR: Could not create an " +
                              "ResultsSubscribeCommand")
            return False

        cfgResProp = threeple.split('.')

        # In .tcl, ResultsSubscribeCommand takes:
        # -ConfigType BfdRouterConfig
        # -ResultType BfdRouterResults
        # -ViewAttributeList {TimeoutCount RxCount}
        sub_cmd.Set("Parent", projHnd)
        sub_cmd.SetCollection("ResultParent", ResultParent)
        sub_cmd.Set("ConfigType", cfgResProp[0])
        sub_cmd.Set("ResultType", cfgResProp[1])
        attrib = str(cfgResProp[2])
        sub_cmd.Set("ViewAttributeList", attrib)  # A string, not really a list
        sub_cmd.Set("Interval", PollingInterval)
        # Don't think I need any of these; they can stay default nothing
        # sub_cmd.Set("ViewName", ViewName)
        # sub_cmd.Set("RecordsPerPage", RecordsPerPage)
        # sub_cmd.SetCollection("FilterList", FilterList)
        # sub_cmd.Set("OutputChildren", OutputChildren)

        pre_datasets_list = project.GetObjects('ResultDataSet')
        pre_datasets_set = set()
        for obj in pre_datasets_list:
            query = obj.GetObject('ResultQuery')
            if (query.Get('ConfigClassId').lower() == cfgResProp[0].lower() and
                    query.Get('ResultClassId').lower() == cfgResProp[1].lower()):
                pre_datasets_set.add(obj.GetObjectHandle())

        sub_cmd.Execute()
        res_data_set = sub_cmd.Get("ReturnedResultDataSet")
        plLogger.LogInfo("res_data_set: " + str(res_data_set))

        post_datasets_list = project.GetObjects('ResultDataSet')
        post_datasets_set = set()
        for obj in post_datasets_list:
            query = obj.GetObject('ResultQuery')
            if (query.Get('ConfigClassId').lower() == cfgResProp[0].lower() and
                    query.Get('ResultClassId').lower() == cfgResProp[1].lower()):
                post_datasets_set.add(obj.GetObjectHandle())

        created_set = post_datasets_set - pre_datasets_set
        assert(len(created_set) == 1)

        for hdlDataSet in created_set:
            oneSub = {"ResultDatasetHandle": hdlDataSet, "ValueIdleTimeout": ValueIdleTimeout,
                      "EnableCondition": EnableCondition, "Terminal": terminal, "Data": [],
                      "ResultParent": ResultParent, "ConfigType": cfgResProp[0],
                      "ResultType": cfgResProp[1], "ViewAttributeList": cfgResProp[2]}
            subList.append(oneSub)

        sub_cmd.MarkDelete()

    plLogger.LogInfo("Finshed SetupSubscriptionCommand")
    return True


def reset():
    return True
