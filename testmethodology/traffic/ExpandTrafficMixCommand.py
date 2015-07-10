from StcIntPythonPL import *
import spirent.methodology.utils.tag_utils as tag_utils
import spirent.methodology.utils.json_utils as json_utils
import spirent.methodology.utils.data_model_utils as data_utils


PKG = "spirent.methodology"
PKG_TRF = PKG + ".traffic"


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTemplateMix, TrafficMixTagName, Load, LoadUnit):
    return ''


# FIXME: handle lists of StmTemplateMix objects?
# TagName, Load, LoadUnits
def run(StmTemplateMix, TrafficMixTagName, Load, LoadUnit):
    '''
    StmTemplateMix is the handle to a StmTrafficMix object (just one object)
    TrafficMixTagName is the name of the tag associated with the StmTrafficMix
    object(s) Load is the traffic load for the entire Mix as the aggregate
    (however, consider how that load is applied to various components and how
    many streams are defined by a given component).
    LoadUnit defines the units context that the Load parameter belongs.

    Within the StmTrafficMix' MixInfo property is the information that
    describes the contents of the Mix. The format for this information is
    JSON. Examples follow:


    Simple east-west traffic with weighted count:
    --------------------------------------------
    {
        "load": 250,
        "loadUnits": "FRAMES_PER_SECOND",
        "components": [
            {
                "baseTemplateFile": "Ipv4_Stream.xml",
                "weight": 75,
                "staticValue": 0,
                "useStaticValue": False,
                "postExpandModify": [
                    {
                        "streamBlockExpand": {
                            "endpointMapping": {
                                "srcBindingTagList": ["East_Ipv4If"],
                                "dstBindingTagList": ["West_Ipv4If"]
                            }
                        }
                    }
                ]
            }
        ]
    }


    Bidirectional east-west traffic with static count:
    -------------------------------------------------
    {
        "load": 250,
        "loadUnits": "FRAMES_PER_SECOND",
        "components": [
            {
                "baseTemplateFile": "Ipv4_Stream.xml",
                "weight": 0,
                "staticValue": 80,
                "useStaticValue": True,
                "postExpandModify": [
                    {
                        "streamBlockExpand": {
                            "endpointMapping": {
                                "srcBindingTagList": ["East_Ipv4If"],
                                "dstBindingTagList": ["West_Ipv4If"],
                                "bidirectional": True
                            }
                        }
                    }
                ]
            }
        ]
    }


    Mesh (for say four devices) on one port:
    (Note that dstBindingTagList is used,
     but is the same as srcBindingTagList.)
    ---------------------------------------
    {
        "load": 250,
        "loadUnits": "FRAMES_PER_SECOND",
        "components": [
            {
                "baseTemplateFile": "AMeshTemplate.xml",
                "weight": 75,
                "staticValue": 0,
                "useStaticValue": False,
                "postExpandModify": [
                    {
                        "streamBlockExpand": {
                            "endpointMapping": {
                                "srcBindingTagList": ["East Ipv4If"],
                                "dstBindingTagList": ["East Ipv4If"]
                            }
                        }
                    }
                ]
            }
        ]
    }

    '''
    plLogger = PLLogger.GetLogger("methodology")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()
    this_cmd = get_this_cmd()

    obj_list = []
    if StmTemplateMix:
        obj_list = CCommandEx.ProcessInputHandleVec('StmTrafficMix',
                                                    [StmTemplateMix])
    if TrafficMixTagName:
        obj_list = obj_list + tag_utils.get_tagged_objects_from_string_names(
            [TrafficMixTagName])
    if len(obj_list) == 0:
        err = "Neither StmTrafficMix nor TrafficMixTagName " \
              "specified a valid StmTrafficMix object."
        plLogger.LogError(err)
        this_cmd.Set('Status', err)
        return False

    for trf_mix in obj_list:
        tmi = trf_mix.Get('MixInfo')
        if tmi == '':
            err = "MixInfo is empty"
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        err_str = json_utils.validate_json(
            tmi, this_cmd.Get('MixInfoJsonSchema'))
        if err_str != "":
            err = "MixInfo in the StmTrafficMix does not conform to the " \
                  "schema " + this_cmd.Get('MixInfoJsonSchema')
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False
        err_str, mix_data = json_utils.load_json(tmi)
        if err_str != "":
            plLogger.LogError(err_str)
            this_cmd.Set("Status", err_str)
            return False
        mix_comp_set = mix_data.get("components")
        if mix_comp_set is None:
            err = "Invalid JSON in MixInfo: MixInfo does not " \
                  "contain components."
            plLogger.LogError(err)
            this_cmd.Set('Status', err)
            return False

        # Expand the StmTemplateConfig objects
        template_list = trf_mix.GetObjects('StmTemplateConfig')

        for template, mix_comp in zip(template_list, mix_comp_set):

            expand_obj = mix_comp.get('expand')
            target_tag_list = \
                expand_obj.get('targetTagList') if expand_obj else None
            copies_per_parent = \
                expand_obj.get('copiesPerParent') if expand_obj else None
            src_tag_list = \
                expand_obj.get('srcTagList') if expand_obj else None

            # Should be validated by schema, but leaving it just in case
            if expand_obj is not None and target_tag_list is None:
                err = 'Error in {}: expand does not ' \
                    'have required targetTagList'.format(template.Get('Name'))
                plLogger.LogError(err)
                this_cmd.Set('Status', err)
                return False

            # At this point, target_tag_list is None if we didn't find a valid
            # expand tag (for raw stream blocks)

            # Note that the streamblock generated for a raw streamblock will
            # not be project-based.

            proj_sb = template.GetObject("StreamBlock",
                                         RelationType("GeneratedObject"))
            if proj_sb is not None:
                err_str = "Cannot expand StreamBlock template, " + \
                    "StreamBlock already exists. Use " + \
                    PKG + "DeleteTemplatesAndGenerated" + \
                    "ObjectsCommand to clean up generated " + \
                    "objects before expanding."
                plLogger.LogError(err_str)
                this_cmd.Set("Status", err_str)
                return False

            cmd = ctor.CreateCommand(PKG + ".ExpandTemplateCommand")
            cmd.SetCollection("StmTemplateConfigList",
                              [template.GetObjectHandle()])
            # If it is a raw stream block, the target tag list is set
            if target_tag_list is not None:
                cmd.SetCollection('TargetTagList', target_tag_list)
            if copies_per_parent is not None:
                cmd.Set('CopiesPerParent', copies_per_parent)
            if src_tag_list is not None:
                cmd.SetCollection('SrcTagList', src_tag_list)
            cmd.Execute()
            pf_state = cmd.Get('PassFailState')
            status = cmd.Get('Status')
            cmd.MarkDelete()
            if pf_state == 'FAILED':
                err = '{}.ExpandTemplateCommand failed: {}' \
                    .format(PKG, status)
                plLogger.LogError(err)
                this_cmd.Set('Status', err)
                return False

            all_sb_list = template.GetObjects('StreamBlock',
                                              RelationType('GeneratedObject'))
            if not all_sb_list:
                err = 'Template {} ({}) did not contain stream blocks' \
                    .format(template.Get('Name'), template.GetObjectHandle())
                plLogger.LogError(err)
                this_cmd.Set('Status', err)
                return False
            proj_sb_list = [x for x in all_sb_list
                            if x.GetParent().IsTypeOf('Project')]
            if len(proj_sb_list) > 1:
                err_str = "Handling of more than one Project-level streamblock by the " + \
                    "ExpandTrafficMixCommand is not supported."
                plLogger.LogError(err_str)
                this_cmd.Set("Status", err_str)
                return False
            for sb in all_sb_list:

                # Retrieve all tags for this streamblock
                sb_tag_list = sb.GetObjects('Tag', RelationType('UserTag'))

                plLogger.LogDebug(show_prop_values("sb_tag_list", sb_tag_list))

                # Gather the endpoints and set up the project-level
                # streamblock. If there aren't any endpoints specified, this
                # is probably a raw streamblock.

                # Perform each expand op...
                for post_expand in mix_comp.get('postExpandModify', []):

                    # Get the streamBlockExpand entry...
                    sb_expand = post_expand.get('streamBlockExpand')
                    if sb_expand is None:
                        continue

                    # Configure the relations and keep track of
                    # src and dst bindings.  Need to handle SrcBinding
                    # and DstBinding depending on the trafficPattern and
                    # the number of bound endpoints.
                    ep_map = sb_expand.get('endpointMapping', None)
                    if ep_map is None:
                        continue
                    bidirectional = ep_map.get("bidirectional", False)
                    src_ep_tag_list = ep_map.get("srcBindingTagList", [])
                    dst_ep_tag_list = ep_map.get("dstBindingTagList", [])

                    if bidirectional:
                        src_ep_tag_list_list = [src_ep_tag_list, dst_ep_tag_list]
                        dst_ep_tag_list_list = [dst_ep_tag_list, src_ep_tag_list]
                    else:
                        src_ep_tag_list_list = [src_ep_tag_list]
                        dst_ep_tag_list_list = [dst_ep_tag_list]

                    src_tagged = []
                    dst_tagged = []
                    for src_ep_tag_list, dst_ep_tag_list in \
                            zip(src_ep_tag_list_list, dst_ep_tag_list_list):
                        src_tagged = tag_utils.get_tagged_objects_from_string_names(
                            src_ep_tag_list)
                        dst_tagged = tag_utils.get_tagged_objects_from_string_names(
                            dst_ep_tag_list)

                        relation_list = ["ParentChild", "GeneratedObject"]

                        src_list = []
                        src_bind_list = ep_map.get("srcBindingClassList", None)
                        if src_bind_list:
                            for src in src_tagged:
                                data_utils.rsearch(src, src_bind_list, relation_list, src_list)
                        else:
                            src_list = src_tagged

                        dst_list = []
                        dst_bind_list = ep_map.get("dstBindingClassList", None)
                        if dst_bind_list:
                            for dst in dst_tagged:
                                data_utils.rsearch(dst, dst_bind_list, relation_list, dst_list)
                        else:
                            dst_list = dst_tagged

                        src_count = len(src_list)
                        dst_count = len(dst_list)
                        plLogger.LogDebug(show_prop_values('src_ep', src_list))
                        plLogger.LogDebug(show_prop_values('dst_ep', dst_list))

                        if src_count == 0 or dst_count == 0:
                            err = "Skipping endpoint binding for " \
                                  "streamblock in template: {}" \
                                  " due to either no tagged sources or " \
                                  "destinations.".format(template.Get("Name"))
                            plLogger.LogError(err)
                            get_this_cmd().Set('Status', err)
                            return False

                        # Update the Project-level streamblock's endpoint
                        # bindings based on the src_list and dst_list and the
                        # trafficPattern

                        if sb.Get("TrafficPattern") == "PAIR":
                            min_count = min(src_count, dst_count)
                            if src_count == 1:
                                plLogger.LogDebug("Streamblocks are configured between " +
                                                  "a src endpoint and all dst end" +
                                                  "point.  src_list has " +
                                                  str(src_count) + " dst_list has " +
                                                  str(dst_count))
                                for ep in dst_list:
                                    sb.AddObject(src_list[0],
                                                 RelationType("SrcBinding"))
                                    sb.AddObject(ep, RelationType("DstBinding"))
                            elif dst_count == 1:
                                plLogger.LogDebug("Streamblocks are configured between " +
                                                  "all src endpoint and a dst end" +
                                                  "point.  src_list has " +
                                                  str(src_count) + " dst_list has " +
                                                  str(dst_count))
                                for ep in src_list:
                                    sb.AddObject(ep, RelationType("SrcBinding"))
                                    sb.AddObject(dst_list[0],
                                                 RelationType("DstBinding"))
                            else:
                                if src_count != dst_count:
                                    plLogger.LogDebug("Streamblocks are configured " +
                                                      "between endpoint pairs until " +
                                                      "one side runs out of endpoints: " +
                                                      "src_list has " + str(src_count) +
                                                      " dst_list has " + str(dst_count))
                                index = 0
                                for ep in src_list:
                                    if index < min_count:
                                        sb.AddObject(ep, RelationType("SrcBinding"))
                                        index = index + 1
                                index = 0
                                for ep in dst_list:
                                    if index < min_count:
                                        sb.AddObject(ep, RelationType("DstBinding"))
                                        index = index + 1
                        else:
                            # BACKBONE or FULLMESH
                            for ep in src_list:
                                sb.AddObject(ep, RelationType("SrcBinding"))
                            for ep in dst_list:
                                sb.AddObject(ep, RelationType("DstBinding"))

                    parent = sb.GetParent()
                    if parent.IsTypeOf('Project'):
                        # Call StreamBlockExpandCommand
                        exp_cmd = ctor.CreateCommand("StreamBlockExpandCommand")
                        exp_cmd.SetCollection("StreamBlockList",
                                              [sb.GetObjectHandle()])
                        exp_cmd.Execute()
                        if exp_cmd.Get("State") == "FAILED":
                            err_str = "Failed to expand Project-level streamblock: " + \
                                sb.Get("Name") + " with handle: " + \
                                str(sb.GetObjectHandle())
                            plLogger.LogError(err_str)
                            this_cmd.Set("Status", err_str)
                            exp_cmd.MarkDelete()
                            return False
                        exp_cmd.MarkDelete()

                        sb_hdl_list = exp_cmd.GetCollection("ExpandedStreamBlockList")
                        gen_sb_list = [hnd_reg.Find(x) for x in sb_hdl_list]
                    else:
                        # For the case of port-based, just return the one
                        gen_sb_list = [sb]
                    for sb in gen_sb_list:
                        if sb is None:
                            continue
                        plLogger.LogDebug("adding gen sb: " + sb.Get("Name") +
                                          " with handle: " + str(sb))
                        template.AddObject(sb, RelationType("GeneratedObject"))

                        # Tag the duplicated port-level streamblock with
                        # original's tags
                        if parent.IsTypeOf('Project'):
                            for tag in sb_tag_list:
                                sb.AddObject(tag, RelationType('UserTag'))
                        dst_list = sb.GetObjects('Scriptable',
                                                 RelationType('DstBinding'))
                        dst_port_map = {}

                        # Go through each destination endpoint and find the port
                        for dst_ep in dst_list:
                            walk = dst_ep
                            # If we've walked to Project we've run out of parents
                            while not walk.IsTypeOf('Project'):
                                if walk.IsTypeOf('EmulatedDevice'):
                                    port = walk.GetObject('Port',
                                                          RelationType('AffiliationPort'))
                                    if port.GetObjectHandle() not in dst_port_map:
                                        dst_port_map[port.GetObjectHandle()] = port
                                    break
                                else:
                                    walk = walk.GetParent()
                        for port in dst_port_map.itervalues():
                            sb.AddObject(port, RelationType('ExpectedRx'))

        # Allocate the Load based on the Weight
        cmd = ctor.CreateCommand(PKG_TRF + ".AllocateTrafficMixLoad")
        cmd.Set("Load", float(Load))
        cmd.Set("LoadUnit", LoadUnit)
        cmd.Set("StmTrafficMix", trf_mix.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()

    return True


def reset():
    return True


def get_prop_values(obj_list, prop='Name'):
    return [t.Get(prop) for t in obj_list]


def show_prop_values(header, obj_list, prop='Name'):
    return '{}: {}'.format(header,
                           ', '.join(get_prop_values(obj_list, prop)))
