from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils
from spirent.core.utils.scriptable import AutoCommand
from spirent.methodology.manager.utils.methodology_manager_utils \
    import MethodologyManagerUtils as mm_utils


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(RouterTagList, BgpImportParamsTagName, CreatedRoutesTagName):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Validate BgpImportRoutesCommand")

    if not RouterTagList:
        return "Invalid RouterTagList passed in"

    if not BgpImportParamsTagName:
        return "Invalid BgpImportParamsTagName passed in"

    return ""


def run(RouterTagList, BgpImportParamsTagName, CreatedRoutesTagName):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogInfo(" Run BgpImportRoutesCommand")
    this_cmd = get_this_cmd()

    if not BgpImportParamsTagName:
        return "Invalid BgpImportParamsTagName passed in"

    router_obj_list = tag_utils.get_tagged_objects_from_string_names(RouterTagList)
    # Turn into handles
    router_list = []
    for router_obj in router_obj_list:
        if router_obj.IsTypeOf('EmulatedDevice'):
            router_list.append(router_obj)
        elif routerObj.IsTypeOf('RouterConfig'):
            router_list.append(router_obj.GetParent().GetObjectHandle())

    if not router_list:
        this_cmd.Set('Status', "RouterTagList does not point to any routers")
        return False

    param_obj_list = \
        tag_utils.get_tagged_objects_from_string_names([BgpImportParamsTagName])

    route_list = []
    for param_obj in param_obj_list:
        # Remove any existing parameter list relations
        exist_list = param_obj.GetObjects('Scriptable',
                                          RelationType('SelectedRouterRelation'))
        for exist in exist_list:
            param_obj.RemoveObject(exist,
                                   RelationType('SelectedRouterRelation'))
        for router in router_list:
            param_obj.AddObject(router,
                                RelationType('SelectedRouterRelation'))
        router_hdl_list = [r.GetObjectHandle() for r in router_list]
        # Create the BgpImportRouteTableCommand
        with AutoCommand('BgpImportRouteTableCommand') as cmd:
            cmd.Set("ImportParams", param_obj.GetObjectHandle())
            # Ensure BLL command gets an absolute path
            abs_path = \
                mm_utils.find_file_across_common_paths(param_obj.Get("FileName"),
                                                       search_templates=True)
            if len(abs_path):
                param_obj.Set("FileName", abs_path)
            cmd.SetCollection("RouterList", router_hdl_list)
            cmd.Set("DeleteRoutes", "NO")
            cmd.Execute()
            cmd_state = cmd.Get('State')
            cmd_status = cmd.Get('Status')
            if cmd_state != 'COMPLETED':
                this_cmd.Set('Status', cmd_status)
                return False

            route_list = param_obj.GetObjects('BgpRouteConfig',
                                              RelationType('WizardGenerated'))
            if not route_list:
                this_cmd.Set('Status', 'Failed to generate any '
                             'route objects for {}'.format(param_obj.Get('Name')))
                return False
            tag_wizgenerated_as_created(param_obj, CreatedRoutesTagName)

    return True


def reset():

    return True


def tag_wizgenerated_as_created(param_obj, CreatedRoutesTagName):
    wizGenRoutes = param_obj.GetObjects("Scriptable",
                                        RelationType("WizardGenerated"))
    wizGenRoutes += param_obj.GetObjects("Scriptable",
                                         RelationType("WizardGeneratedObject"))
    for obj in wizGenRoutes:
        # Tag all the "WizardGenerated" routes with the tag name requested via
        # this command's CreatedRoutesTagName property.
        if CreatedRoutesTagName:
            tag_utils.add_tag_to_object(obj, CreatedRoutesTagName)
    return True
