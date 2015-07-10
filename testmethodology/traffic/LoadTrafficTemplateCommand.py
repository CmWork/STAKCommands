from StcIntPythonPL import *
from spirent.core.utils.scriptable import AutoCommand
import xml.etree.ElementTree as etree
from spirent.methodology.LoadTemplateCommand \
    import validate_contained_cmds, \
    config_contained_cmds


PKG = "spirent.methodology"


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def init():
    '''
    Init is needed since the default to expand for traffic is False
    '''
    this_cmd = get_this_cmd()
    this_cmd.Set('AutoExpandTemplate', False)
    this_cmd.SetCollection('TargetTagList', [])
    return True


def validate(CopiesPerParent, TargetTagList, TemplateXml, TemplateXmlFileName,
             TagPrefix, AutoExpandTemplate, EnableLoadFromFileName,
             Weight, StmTemplateMix):
    return validate_contained_cmds(get_this_cmd())


def run(CopiesPerParent, TargetTagList, TemplateXml, TemplateXmlFileName,
        TagPrefix, AutoExpandTemplate, EnableLoadFromFileName,
        Weight, StmTemplateMix):
    plLogger = PLLogger.GetLogger("LoadTrafficTemplateCommand")
    this_cmd = get_this_cmd()
    tmpl_cfg_hdl = 0
    with AutoCommand(PKG + ".LoadTemplateCommand") as load_cmd:
        load_cmd.Set('CopiesPerParent', CopiesPerParent)
        load_cmd.SetCollection('TargetTagList', TargetTagList)
        load_cmd.Set('TemplateXml', TemplateXml)
        load_cmd.Set('TemplateXmlFileName', TemplateXmlFileName)
        load_cmd.Set('TagPrefix', TagPrefix)
        load_cmd.Set('AutoExpandTemplate', AutoExpandTemplate)
        load_cmd.Set('EnableLoadFromFileName', EnableLoadFromFileName)
        load_cmd.Set('StmTemplateMix', StmTemplateMix)
        load_cmd.Execute()
        if 'COMPLETED' != load_cmd.Get('State'):
            this_cmd.Set('State', load_cmd.Get('State'))
            this_cmd.Set('Status', load_cmd.Get('Status'))
            return False
        tmpl_cfg_hdl = load_cmd.Get('StmTemplateConfig')

    hnd_reg = CHandleRegistry.Instance()
    tmpl_cfg = hnd_reg.Find(tmpl_cfg_hdl)
    if tmpl_cfg is None:
        plLogger.LogError('Failed to create valid StmTemplateConfig object')
        return False

    # Configure child cmd input handles
    config_contained_cmds(get_this_cmd(), tmpl_cfg)

    # Insert weight into the parent table
    traf_mix = hnd_reg.Find(StmTemplateMix)
    if traf_mix is None:
        plLogger.LogError('Invalid StmTemplateMix handle ' + str(StmTemplateMix))
        return False
    # Add weight to traf_mix table
    mix_elem = etree.fromstring(traf_mix.Get('MixInfo'))
    wl_str = mix_elem.get('WeightList')
    if wl_str is None:
        plLogger.LogError('Parent StmTemplateMix object has no Weight table')
        return False
    wl_str = wl_str + ' ' + str(Weight) if len(wl_str) != 0 else str(Weight)
    mix_elem.set('WeightList', wl_str)
    traf_mix.Set('MixInfo', etree.tostring(mix_elem))

    # Return the created template (in case this was called in isolation
    # instead of as part of a CreateTrafficMix group
    this_cmd.Set("StmTemplateConfig", tmpl_cfg.GetObjectHandle())

    return True


def on_complete(failed_commands):
    return True


def reset():
    return True
