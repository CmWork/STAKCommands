from StcIntPythonPL import *
import xml.etree.ElementTree as etree
from collections import defaultdict
from spirent.core.utils.scriptable import AutoCommand
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.utils.data_model_utils as dm_utils


PKG = "spirent.methodology"
PKG_RTG = PKG + ".routing"
TEMP_TRG_TAG = "ExpandRouteMixCommand_temporary_target_tag"


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def get_routers(TargetObjectList, TargetObjectTagList):
    plLogger = PLLogger.GetLogger("methodology")
    routers_dict = defaultdict(list)
    this_cmd = get_this_cmd()

    rtr_list = []
    rtr_list = dm_utils.get_class_objects(TargetObjectList, TargetObjectTagList, ["RouterConfig"])

    if len(rtr_list) == 0:
        err = "No routers found in TargetObjectList or TargetObjectTagList"
        plLogger.LogError(err)
        this_cmd.Set('Status', err)
        return {}

    # Build the output dictionary based on router type
    for rtr in rtr_list:
        # Use the CMeta to get the correct form of the class name
        meta_dict = CMeta.GetClassMeta(rtr)
        routers_dict[meta_dict["name"]].append(rtr)
    return routers_dict


def process_wizard_args(tmpl_cfg, wiz_list):
    '''
    Inputs: Template config and list of wizard dictionaries containing
    targetTagList, srcObjectTagName, createdRoutesTagName, commandName
    '''
    plLogger = PLLogger.GetLogger('methodology')
    this_cmd = get_this_cmd()
    for wiz in wiz_list:
        targ_tag_list = wiz.get('targetTagList')
        src_tag = wiz.get('srcObjectTagName')
        route_tag_name = wiz.get('createdRoutesTagName')
        command_name = wiz.get('commandName')
        # FIXME: It seems curious that the bllWizardExpand section has a
        # target tag list, when the command itself has the same list as a
        # input property -- evaluate whether this can be eliminated
        if not targ_tag_list:
            err = "No target tag list given"
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        if not src_tag:
            err = "No source object tag given"
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        if not command_name:
            err = "Command name not specified"
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        rtr_list = tag_utils.get_tagged_objects_from_string_names(targ_tag_list)
        # Remove duplicates by using an ordered dictionary
        rtr_list = dm_utils.remove_dup_scriptable(rtr_list)
        if len(rtr_list) == 0:
            err = "targetTagList results in an empty list"
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        pf_state, status = 'FAILED', ''
        with AutoCommand(PKG + '.ExpandTemplateCommand') as cmd:
            cmd.SetCollection('StmTemplateConfigList',
                              [tmpl_cfg.GetObjectHandle()])
            cmd.SetCollection('SrcTagList', [src_tag])
            cmd.Execute()
            pf_state = cmd.Get('PassFailState')
            status = cmd.Get('Status')
        if pf_state == 'FAILED':
            err = '{}.ExpandTemplateCommand failed: {}' \
                .format(PKG, status)
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        # Call the wizard once the configuration is loaded
        cfg_obj_list = tag_utils.get_tagged_objects_from_string_names([src_tag])
        if not cfg_obj_list:
            err = 'Failed to load expected configuration object for {}' \
                .format(tmpl_cfg.Get('Name'))
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        if len(cfg_obj_list) > 1:
            err = 'More than one configuration objects loaded from {}' \
                .format(tmpl_cfg.Get('Name'))
            plLogger.LogInfo(err)
        # We check the object list just to prevent bad input. The target
        # command operates on the tag only, so we don't need to manipulate the
        # objects beyond getting the count
        pf_state, status = 'FAILED', ''
        tag_created = False
        if not route_tag_name:
            route_tag_name = 'Tmp Imported Routes'
            tag_created = True
        with AutoCommand(command_name) as cmd:
            # Set the parameters depending on the command used
            if 'Import' in command_name:
                cmd.SetCollection('RouterTagList', targ_tag_list)
                cmd.Set('BgpImportParamsTagName', src_tag)
                cmd.Set('CreatedRoutesTagName', route_tag_name)
            elif 'Prefix' in command_name:
                cmd.SetCollection('RouterTagList', targ_tag_list)
                cmd.Set('SrcObjectTagName', src_tag)
                cmd.Set('CreatedRoutesTagName', route_tag_name)
            cmd.Execute()
            pf_state = cmd.Get('PassFailState')
            status = cmd.Get('Status')
        if pf_state == 'FAILED':
            err = '{} failed: {}'.format(command_name, status)
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        # After a successful run, we need to associate the newly-created
        # routes to the template with the GeneratedObject relation
        added_route_list = \
            tag_utils.get_tagged_objects_from_string_names([route_tag_name])
        for route in added_route_list:
            tmpl_cfg.AddObject(route, RelationType('GeneratedObject'))
        # If we created a temporary tag, delete it here
        if tag_created:
            tag_obj = tag_utils.get_tag_object(route_tag_name)
            tag_obj.MarkDelete()
    return True


def process_route_args(tmpl_cfg, routers_dict):
    '''
    Purpose: Calls the ExpandTemplateCommand for each protocol in the
    configuration
    Inputs: Template config and component section from the templatemix
    '''
    plLogger = PLLogger.GetLogger("methodology")
    this_cmd = get_this_cmd()

    root = etree.fromstring(tmpl_cfg.Get('TemplateXml'))

    # For each kind of RouterConfig, check this StmTemplateConfig's
    # XML tree for that classname.
    for router_type in routers_dict:
        # Remove serializationBase from the XML
        serial_ele_list = root.findall('.//*[@serializationBase="true"]')
        for ele in serial_ele_list:
            if 'serializationBase' in ele.attrib:
                ele.attrib.pop('serializationBase')
        ele_list = root.findall(".//" + router_type)
        if not ele_list:
            continue
        # We found, for instance, a BgpRouterConfig both in the
        # template XML, and in StmProtocolMix's objects, so we
        # expand this StmTemplateConfig onto all those objects

        if len(ele_list) != 1:
            err = "More than one {} found. That's weird." \
                .format(router_type)
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        router_ele = ele_list[0]

        # Mark all children with serializationBase
        for child in router_ele:
            plLogger.LogInfo("process element: " + str(child))
            if child.tag == "Relation":
                # Except for Relation elements
                continue
            # Check for Ipv4NetworkBlocks or Ipv6NetworkBlocks
            ipv4_net_block = child.find(".//Ipv4NetworkBlock")
            ipv6_net_block = child.find(".//Ipv6NetworkBlock")
            if (ipv4_net_block is not None and len(ipv4_net_block)) or \
               (ipv6_net_block is not None and len(ipv6_net_block)):
                child.attrib["serializationBase"] = "true"
            else:
                plLogger.LogWarn("Skipping object of type " +
                                 child.tag)

        # Make temporary tags for this instance of ExpandRouteMixCommand
        tag_obj = tag_utils.get_tag_object(TEMP_TRG_TAG)

        # Tag all routerConfigs in the dictionary of this type
        # with a temporary target tag, since ExpandTemplateCommand
        # needs that
        for router in routers_dict[router_type]:
            tag_utils.add_tag_to_object(router, TEMP_TRG_TAG)
        tmpl_cfg.Set("TemplateXml", etree.tostring(root))

        pf_state, status = 'FAILED', ''
        with AutoCommand(PKG + '.ExpandTemplateCommand') as cmd:
            cmd.SetCollection('StmTemplateConfigList',
                              [tmpl_cfg.GetObjectHandle()])
            cmd.SetCollection("TargetTagList", [TEMP_TRG_TAG])
            cmd.Execute()
            pf_state = cmd.Get('PassFailState')
            status = cmd.Get('Status')
        if pf_state == 'FAILED':
            err = '{}.ExpandTemplateCommand failed: {}' \
                .format(PKG, status)
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        # After expand of routes is done, remove the tag from the target
        # router objects
        tag_obj.MarkDelete()
    return True


def validate(TargetObjectList, TargetObjectTagList, SrcObjectList,
             SrcObjectTagList, RouteCount):
    if RouteCount < 1:
        err_str = "RouteCount must be at least 1."
        return err_str
    return ''


def run(TargetObjectList, TargetObjectTagList, SrcObjectList,
        SrcObjectTagList, RouteCount):
    plLogger = PLLogger.GetLogger("methodology")
    this_cmd = get_this_cmd()

    # Process targets for RouterConfigs
    routers_dict = get_routers(TargetObjectList, TargetObjectTagList)
    # If we get empty dictionary here, error has already been created
    if not routers_dict:
        return False

    # Process sources for RouteConfig XMLs
    rmix_list = []
    if SrcObjectList:
        rmix_list = CCommandEx.ProcessInputHandleVec('StmTemplateMix',
                                                     SrcObjectList)
    if SrcObjectTagList:
        rmix_list = rmix_list + \
            tag_utils.get_tagged_objects_from_string_names(SrcObjectTagList)
    rmix_list = dm_utils.remove_dup_scriptable(rmix_list)
    if len(rmix_list) == 0:
        err = "Neither SrcObjectList nor SrcObjectTagList " \
            "specified a valid SrcObjectList object."
        plLogger.LogError(err)
        this_cmd.Set('Status', err)
        return False

    # Each RouteConfig we find in the StmTemplateMix'es StmTemplateConfigs is
    # a source point to use in a ExpandTemplateCommand (with targets being
    # routers from the StmProtocolMix)
    for rmix in rmix_list:
        r_mi = rmix.Get('MixInfo')
        if r_mi == '':
            err = "MixInfo is empty for {}".format(rmix.Get('Name'))
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        err_str = json_utils.validate_json(r_mi,
                                           this_cmd.Get('MixInfoJsonSchema'))
        if err_str != '':
            err = "MixInfo in the StmTemplateMix does not conform to the " \
                  "schema " + this_cmd.Get('MixInfoJsonSchema')
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        err_str, mix_data = json_utils.load_json(r_mi)
        if err_str != "":
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False
        mix_comp_list = mix_data.get('components')
        if mix_comp_list is None:
            err = "Invalid JSON in MixInfo: MixInfo does not " \
                  "contain components."
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        tmpl_cfg_list = rmix.GetObjects('StmTemplateConfig')
        for tmpl_cfg, mix_comp in zip(tmpl_cfg_list, mix_comp_list):
            # At this point, we have the template and associated component
            # entry, and we need to determine what kind of template file is
            # being loaded

            # First check the expand
            exp_list = mix_comp.get('postExpandModify', [])
            wiz_list = []
            for exp in exp_list:
                wiz = exp.get('bllWizardExpand')
                if wiz is None:
                    continue
                wiz_list.append(wiz)
            if wiz_list:
                if not process_wizard_args(tmpl_cfg, wiz_list):
                    # Error message handled in called functions
                    return False
            else:
                if not process_route_args(tmpl_cfg, routers_dict):
                    # Error message handled in called function
                    return False

    # After the routes are created, call allocate for each argument
    with AutoCommand(PKG_RTG + '.AllocateRouteMixCountCommand') as cmd:
        cmd.SetCollection('RouteMixList', [r.GetObjectHandle() for r in rmix_list])
        cmd.Set('RouteCount', RouteCount)
        cmd.Execute()
        pf_state = cmd.Get('PassFailState')
        status = cmd.Get('Status')
    if pf_state == 'FAILED':
        err = '{}.AllocateRouteMixCountCommand failed: {}' \
            .format(PKG_RTG, status)
        plLogger.LogError(err)
        this_cmd.Set('Status', err)
        return False
    return True


def reset():
    return True
