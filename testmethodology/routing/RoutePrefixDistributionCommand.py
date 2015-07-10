from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(RouterTagList, SrcObjectTagName, CreatedRoutesTagName):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Validate RoutePrefixDistributionCommand")

    if not RouterTagList:
        return "Invalid RouterTagList passed in"

    if not SrcObjectTagName:
        return "Invalid SrcObjectTagName passed in"

    return ""


def run(RouterTagList, SrcObjectTagName, CreatedRoutesTagName):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run RoutePrefixDistributionCommand")
    ctor = CScriptableCreator()
    this_cmd = get_this_cmd()

    protocolParamObjs = tag_utils.get_tagged_objects_from_string_names([SrcObjectTagName])
    if len(protocolParamObjs) == 0:
        this_cmd.Set('Status', 'No objects with tag matching SrcObjectTagName')
        return False
    routerObjs = tag_utils.get_tagged_objects_from_string_names(RouterTagList)
    if len(routerObjs) == 0:
        this_cmd.Set('Status', 'No routers with tag in RouterTagList')
        return False

    for protocolParamObj in protocolParamObjs:
        for routerObj in routerObjs:
            if not (routerObj.IsTypeOf('EmulatedDevice') or
                    routerObj.IsTypeOf('RouterConfig')):
                this_cmd.Set('Status', routerObj.Get('Name') + "is of type " +
                             routerObj.GetType() +
                             "should be of type EmulatedDevice or RouterConfig")
                return False
            # Get EmulatedDevice if a RouterConfig tag was passed in
            if routerObj.IsTypeOf('RouterConfig'):
                routerObj = routerObj.GetParent()

            # RouteGenApplyCommand will skip any Emulated Devices that don't have
            # and affiliation port
            if not routerObj.GetObject('Port', RelationType('AffiliationPort')):
                this_cmd.Set('Status', 'EmulatedDevice has no AffiliationPort')
                return False

            # Only EmulatedDevices allowed for SelectedRouterRelation
            protocolParamObj.AddObject(routerObj, RelationType('SelectedRouterRelation'))

        if not protocolParamObj.GetObjects('EmulatedDevice',
                                           RelationType('SelectedRouterRelation')):
            this_cmd.Set('Status', 'No routers specified for routes to be attached to')
            return False

        # Create the RouteGenApplyCommand
        cmd = ctor.CreateCommand("RouteGenApplyCommand")
        cmd.Set("GenParams", protocolParamObj.GetObjectHandle())
        cmd.Set("DeleteRoutesOnApply", "NO")
        cmd.Execute()

        # If RouteGenApplyCommand fails, fail this command
        cmd_state = cmd.Get('State')
        cmd_status = cmd.Get('Status')
        if cmd_state != 'COMPLETED':
            this_cmd.Set('Status', "RouteGenApplyCommand did not complete: " + cmd_status)
            cmd.MarkDelete()
            return False
        cmd.MarkDelete()

        # Verify that routes were created
        num_routes = 0
        routeParamObjs = protocolParamObj.GetObjects('RouteGenParams',
                                                     RelationType('ParentChild'))
        for routeParamObj in routeParamObjs:
            num_routes += len(routeParamObj.GetObjects('Scriptable',
                                                       RelationType('WizardGeneratedObject')))
        if num_routes == 0:
            warn_msg = "Failed to generate any route objects using the RouteGenApplyCommand: " + \
                cmd_status
            this_cmd.Set('Status', warn_msg)
            plLogger.LogWarn(warn_msg)

        routeGenParamObjs = protocolParamObj.GetObjects('RouteGenParams')
        for routeGenParamObj in routeGenParamObjs:
            if CreatedRoutesTagName:
                tag_wizgenerated_as_created(routeGenParamObj, CreatedRoutesTagName)

    return True


def reset():
    return True


def tag_wizgenerated_as_created(routeGenParamObj, CreatedRoutesTagName):

    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug(" RoutePrefixDistributionCommand tag_wizgenerated_as_created start")
    wizGenRoutes = routeGenParamObj.GetObjects("Scriptable",
                                               RelationType("WizardGenerated"))
    wizGenRoutes += routeGenParamObj.GetObjects("Scriptable",
                                                RelationType("WizardGeneratedObject"))
    for obj in wizGenRoutes:
        # Tag all the "WizardGenerated" routes with the tag name requested via this
        # command's CreatedRoutesTagName property.
        if CreatedRoutesTagName:
            tag_utils.add_tag_to_object(obj, CreatedRoutesTagName)
            plLogger.LogDebug("Adding tag " + CreatedRoutesTagName + " to " + obj.Get("Name"))

    plLogger.LogDebug(" RoutePrefixDistributionCommand tag_wizgenerated_as_created end")
    return True
