from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import spirent.methodology.utils.tag_utils as tag_utils


PKG = "spirent.methodology"
PKG_TRF = PKG + ".traffic"


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTemplateMix):
    # plLogger = PLLogger.GetLogger("methodology")
    # this_cmd = get_this_cmd()
    return ''


# FIXME: handle lists of StmTemplateMix objects?
def run(StmTemplateMix):
    plLogger = PLLogger.GetLogger("methodology")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()
    trf_mix = hnd_reg.Find(StmTemplateMix)
    if trf_mix is None:
        plLogger.LogError("TrafficMix with handle " + str(StmTemplateMix) +
                          " was not found")

    tmi = trf_mix.Get('MixInfo')
    if tmi == '':
        plLogger.LogError("MixInfo is empty")
        return False
    root = etree.fromstring(tmi)

    # Expand the StmTemplateConfig objects
    template_list = trf_mix.GetObjects('StmTemplateConfig')
    for template in template_list:
        cmd = ctor.CreateCommand(PKG + ".ExpandTemplateCommand")
        cmd.SetCollection("StmTemplateConfigList",
                          [template.GetObjectHandle()])
        cmd.Execute()
        cmd.MarkDelete()

        # Gather the endpoints
        src_tag_ele_list = root.findall(".//SrcEndpoint")
        plLogger.LogInfo("src_tag_ele_list: " + str(src_tag_ele_list))
        src_tag_list = []
        for src_tag_ele in src_tag_ele_list:
            src_tag_list.append(src_tag_ele.text)
        plLogger.LogInfo("src_tag_list: " + str(src_tag_list))

        dst_tag_ele_list = root.findall(".//DstEndpoint")
        plLogger.LogInfo("dst_tag_ele_list: " + str(dst_tag_ele_list))
        dst_tag_list = []
        for dst_tag_ele in dst_tag_ele_list:
            dst_tag_list.append(dst_tag_ele.text)
        plLogger.LogInfo("dst_tag_list: " + str(dst_tag_list))

        src_count = 0
        src_ep_list = tag_utils.get_tagged_endpoints_given_tag_names(src_tag_list)
        for src_ep in src_ep_list:
            plLogger.LogInfo("src_ep: " + src_ep.Get("Name"))

        if len(src_ep_list) > 0:
            src_count = len(src_ep_list)
        else:
            # Normally this would be had from the src-dst bindings of the
            # TrafficProfile.  However, we don't have those.  Need to
            # figure out what is being associated here.
            pass

        dst_count = 0
        dst_ep_list = tag_utils.get_tagged_endpoints_given_tag_names(dst_tag_list)
        for dst_ep in dst_ep_list:
            plLogger.LogInfo("dst_ep: " + dst_ep.Get("Name"))

        if len(dst_ep_list) > 0:
            dst_count = len(dst_ep_list)
        else:
            # Normally this would be had from the src-dst bindings of the
            # TrafficProfile.  However, we don't hvae those.  Need to
            # figure out what is being associated here.
            pass

        min_count = min(src_count, dst_count)

        # Expand the Project-level StreamBlock
        proj_sb = template.GetObject("StreamBlock",
                                     RelationType("GeneratedObject"))
        if proj_sb is None:
            plLogger.LogInfo("Skipping template " + template.Get("Name") +
                             " as it has no Project-level Streamblock " +
                             "to expand")
            continue
        # Retrieve all tags for this streamblock
        tag_list = proj_sb.GetObjects('Tag', RelationType('UserTag'))
        if len(src_ep_list) > 0 and len(dst_ep_list) > 0:
            plLogger.LogInfo("Expanding proj_sb: " + proj_sb.Get("Name"))

            if proj_sb.Get("TrafficPattern") == "PAIR":
                if src_count == 1:
                    plLogger.LogInfo("Streamblocks are configured between " +
                                     "a source end point and all dest end point." +
                                     " src_list has " + str(src_count) +
                                     " dst_list has " + str(dst_count))
                    for ep in dst_ep_list:
                        proj_sb.AddObject(src_ep_list[0], RelationType("SrcBinding"))
                        proj_sb.AddObject(ep, RelationType("DstBinding"))
                elif dst_count == 1:
                    plLogger.LogInfo("Streamblocks are configured between " +
                                     "all source end point and a dest end point." +
                                     " src_list has " + str(src_count) +
                                     " dst_list has " + str(dst_count))
                    for ep in src_ep_list:
                        proj_sb.AddObject(ep, RelationType("SrcBinding"))
                        proj_sb.AddObject(dst_ep_list[0], RelationType("DstBinding"))
                else:
                    if src_count != dst_count:
                        plLogger.LogInfo("Streamblocks are configured between " +
                                         "endpoint pairs until one side runs " +
                                         "out of endpoints: src_list has " +
                                         str(src_count) + " dst_list has " +
                                         str(dst_count))
                    index = 0
                    for ep in src_ep_list:
                        if index < min_count:
                            proj_sb.AddObject(ep, RelationType("SrcBinding"))
                            index = index + 1
                    index = 0
                    for ep in dst_ep_list:
                        if index < min_count:
                            proj_sb.AddObject(ep, RelationType("DstBinding"))
                            index = index + 1
            else:
                for ep in src_ep_list:
                    proj_sb.AddObject(ep, RelationType("SrcBinding"))
                for ep in dst_ep_list:
                    proj_sb.AddObject(ep, RelationType("DstBinding"))
        else:
            plLogger.LogError("No Src or Dst bindings...fix this to use TLI")

        # Call StreamBlockExpandCommand
        exp_cmd = ctor.CreateCommand("StreamBlockExpandCommand")
        exp_cmd.SetCollection("StreamBlockList",
                              [proj_sb.GetObjectHandle()])
        exp_cmd.Execute()
        exp_cmd.MarkDelete()

        gen_sb_list = exp_cmd.GetCollection("ExpandedStreamBlockList")
        for gen_sb in gen_sb_list:
            sb = hnd_reg.Find(gen_sb)
            if sb is None:
                plLogger.LogError("Invalid handle " + str(gen_sb))
                continue
            plLogger.LogInfo("adding gen sb: " + sb.Get("Name"))
            template.AddObject(sb, RelationType("GeneratedObject"))
            # Tag the duplicated port-level streamblock with original's tags
            for tag in tag_list:
                sb.AddObject(tag, RelationType('UserTag'))
            dst_ep_list = sb.GetObjects('Scriptable',
                                        RelationType('DstBinding'))
            dst_port_map = {}
            # Go through each destination endpoint and find the port
            for dst_ep in dst_ep_list:
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
    mix_elem = etree.fromstring(tmi)
    load = mix_elem.get("Load")
    load_unit = mix_elem.get("LoadUnit")

    cmd = ctor.CreateCommand(PKG_TRF + ".AllocateTrafficMixLoad1Command")
    cmd.Set("Load", load)
    cmd.Set("LoadUnit", load_unit)
    cmd.Set("StmTrafficMix", trf_mix.GetObjectHandle())
    cmd.Execute()
    cmd.MarkDelete()

    return True


def reset():
    return True
