from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
from spirent.methodology.traffictest.utils.AccessControlList import *
# import spirent.methodology.traffic.LoadTrafficTemplateCommand as base


PKG = 'spirent.methodology'
TPKG = PKG + '.traffic'


# FIXME: The following are not yet supported...
#    UDP, IPv6
#    <=, >=, and more than one value for <, and >, for both mac and ip
#    L4port rules: port_from_rule() is not implemented yet
#
#    We may want to use the size of the import table to drive the good/bad stream counts...


acl = None


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(CopiesPerParent, TargetTagList, TemplateXml, TemplateXmlFileName,
             TagPrefix, AutoExpandTemplate, EnableLoadFromFileName,
             StmTemplateMix, Weight, RulesFileName, StreamsPerRule, ConformToAccept):
    global acl
    plLogger = PLLogger.GetLogger('Methodology')
    plLogger.LogDebug('LoadTrafficRulesCommand.validate()')
    # msg = base.validate(CopiesPerParent, TargetTagList, TemplateXml, TemplateXmlFileName,
    #                     TagPrefix, AutoExpandTemplate, EnableLoadFromFileName,
    #                     TrafficMix, Weight)
    # if msg != '':
    #     return msg

    if StreamsPerRule == 0:
        return 'StreamsPerRule cannot be zero.'

    acl = AccessControlList(ConformToAccept)
    return acl.import_rules_file(RulesFileName)


def run(CopiesPerParent, TargetTagList, TemplateXml, TemplateXmlFileName,
        TagPrefix, AutoExpandTemplate, EnableLoadFromFileName,
        StmTemplateMix, Weight, RulesFileName, StreamsPerRule, ConformToAccept):
    global rules
    plLogger = PLLogger.GetLogger('Methodology')
    plLogger.LogDebug('LoadTrafficRulesCommand.run()')

    rule_count = acl.count()
    weight_per_streamblock = Weight / (rule_count * StreamsPerRule)

    # We want to round robin the rules to maximize the variety...
    for i in range(0, StreamsPerRule):
        for ace in acl.ace_list():
            with AutoCommand(TPKG + ".LoadTrafficTemplateCommand") as cmd:
                cmd.Set('CopiesPerParent', CopiesPerParent)
                cmd.SetCollection('TargetTagList', TargetTagList)
                cmd.Set('TemplateXml', TemplateXml)
                cmd.Set('TemplateXmlFileName', TemplateXmlFileName)
                cmd.Set('TagPrefix', TagPrefix)
                cmd.Set('Weight', weight_per_streamblock)
                cmd.Set('AutoExpandTemplate', False)
                cmd.Set('EnableLoadFromFileName', EnableLoadFromFileName)
                cmd.Set('StmTemplateMix', StmTemplateMix)
                cmd.Execute()
                config = cmd.Get('StmTemplateConfig')

            # Form the rules...
            tags_and_property_values = \
                [(TagPrefix + 'ttDstMac', 'RangeModifier.Data', ace.dst_mac()),
                 (TagPrefix + 'ttSrcMac', 'RangeModifier.Data', ace.src_mac()),
                 (TagPrefix + 'ttDstIpAddr', 'RangeModifier.Data', ace.dst_ip()),
                 (TagPrefix + 'ttSrcIpAddr', 'RangeModifier.Data', ace.src_ip()),
                 (TagPrefix + 'ttDstPort', 'RangeModifier.Data', ace.dst_port()),
                 (TagPrefix + 'ttSrcPort', 'RangeModifier.Data', ace.src_port()),
                 ]

            for tag_name, prop_name, value in tags_and_property_values:
                # Skip over "special" indicators for skipped values
                if value is None or value is "" or value == 0:
                    continue
                with AutoCommand(PKG + ".ModifyTemplatePropertyCommand") as mod:
                    mod.Set('StmTemplateConfig', config)
                    mod.SetCollection('TagNameList', [tag_name])
                    mod.SetCollection('PropertyList', [prop_name])
                    mod.SetCollection('ValueList', [value])
                    mod.Execute()

    return True


def reset():
    return True
