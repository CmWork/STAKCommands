from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import spirent.methodology.utils.tag_utils as tag_utils


def enable_preload(streamblock):
    stcSys = CStcSystem.Instance()
    project = stcSys.GetObject("Project")
    ctor = CScriptableCreator()
    preload_profile = project.GetObject("AnalyzerPreloadProfile")
    if preload_profile is None:
        preload_profile = ctor.Create("AnalyzerPreloadProfile", project)
    preload_profile.AddObject(streamblock,
                              RelationType(
                                  "AffiliationAnalyzerPreloadStreamBlock"
                                  )
                              )


def expand_traffic_mix_group(tp_map):
    # tp_map:
    #   { "src_subnets":
    #       [{"traffix_mix": /traffic_mix_hnd/,
    #         "src_tag": /src_tag_hnd/}
    #        {...}, ...]
    #      "dst_tags" = [/dst_tag_hnd/]
    #   }
    plLogger = PLLogger.GetLogger("expand_util")
    hnd_reg = CHandleRegistry.Instance()
    ctor = CScriptableCreator()

    dst_tags = tp_map["dst_tags"]

    dst_count = 0
    dst_ep_list = tag_utils.get_tagged_endpoints_given_tag_names(dst_tags)
    for dst_ep in dst_ep_list:
        plLogger.LogInfo("dst_ep: " + dst_ep.Get("Name"))
    if len(dst_ep_list) > 0:
        dst_count = len(dst_ep_list)
    else:
        raise Exception("no destination device found")

    cur_dst_ep_idx = 0

    for src_subnet in tp_map["src_subnets"]:
        trf_mix_hnd = src_subnet["traffix_mix"]
        trf_mix = hnd_reg.Find(trf_mix_hnd)
        if trf_mix is None:
            plLogger.LogError("TrafficMix with handle " + str(trf_mix_hnd) +
                              " was not found")
        tmi = trf_mix.Get('MixInfo')
        if tmi == '':
            raise Exception("MixInfo is empty")

        # Gather the endpoints
        src_tag = src_subnet["src_tag"]
        src_ep_list = tag_utils.get_tagged_endpoints_given_tag_names([src_tag])
        src_count = len(src_ep_list)
        for src_ep in src_ep_list:
            plLogger.LogInfo("src_ep: " + src_ep.Get("Name"))
        if src_count < 0:
            raise Exception("no source device found")

        # Expand the StmTemplateConfig objects
        template_list = trf_mix.GetObjects('StmTemplateConfig')
        for template in template_list:
            local_dst_ep_idx = cur_dst_ep_idx
            cmd = ctor.CreateCommand("spirent.methodology.ExpandTemplateCommand")
            cmd.SetCollection("StmTemplateConfigList",
                              [template.GetObjectHandle()])
            cmd.Execute()
            cmd.MarkDelete()

            proj_sb = template.GetObject("StreamBlock",
                                         RelationType("GeneratedObject"))
            if proj_sb is None:
                plLogger.LogInfo("Skipping template " + template.Get("Name") +
                                 " as it has no Project-level Streamblock " +
                                 "to expand")
                continue
            # enable preload
            enable_preload(proj_sb)
            # Retrieve all tags for this streamblock
            tag_list = proj_sb.GetObjects('Tag', RelationType('UserTag'))
            plLogger.LogInfo("Expanding proj_sb: " + proj_sb.Get("Name"))
            if proj_sb.Get("TrafficPattern") == "PAIR":
                for ep in src_ep_list:
                    if local_dst_ep_idx < dst_count:
                        proj_sb.AddObject(ep, RelationType("SrcBinding"))
                        proj_sb.AddObject(dst_ep_list[local_dst_ep_idx],
                                          RelationType("DstBinding"))
                        local_dst_ep_idx += 1
                    else:
                        break
            else:
                for ep in src_ep_list:
                    proj_sb.AddObject(ep, RelationType("SrcBinding"))
                for ep in dst_ep_list:
                    proj_sb.AddObject(ep, RelationType("DstBinding"))

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
                cur_dst_ep_list = sb.GetObjects('Scriptable',
                                                RelationType('DstBinding'))
                dst_port_map = {}
                # Go through each destination endpoint and find the port
                for dst_ep in cur_dst_ep_list:
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
        cur_dst_ep_idx += src_count

        # Allocate the Load based on the Weight
        mix_elem = etree.fromstring(tmi)
        load = mix_elem.get("Load")
        load_unit = mix_elem.get("LoadUnit")

        cmd = ctor.CreateCommand("spirent.methodology.traffic.AllocateTrafficMixLoad1Command")
        cmd.Set("Load", load)
        cmd.Set("LoadUnit", load_unit)
        cmd.Set("StmTrafficMix", trf_mix.GetObjectHandle())
        cmd.Execute()
        cmd.MarkDelete()
