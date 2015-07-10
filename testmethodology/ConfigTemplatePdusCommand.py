from StcIntPythonPL import *
import xml.etree.ElementTree as etree
import spirent.methodology.utils.xml_config_utils as xml_utils


PKG = 'spirent.methodology'


def get_this_cmd():
    hnd_reg = CHandleRegistry.Instance()
    return hnd_reg.Find(__commandHandle__)


def validate(StmTemplateConfig, TemplateElementTagNameList, PduPropertyList, PduValueList):
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('ConfigTemplatePdusCommand.validate')
    return ''


def run(StmTemplateConfig, TemplateElementTagNameList, PduPropertyList, PduValueList):
    '''
        StmTemplateConfig is the container for the StreamBlock's template.
        TemplateElementTagNameList holds a list of tag names that associate with StreamBlocks in
                the template that are to be targeted for modification.
        PduInfoList represents a list of PDU information to update in the FrameConfig
                for all StreamBlocks in the template that associate with any of the
                given tag names.
    '''
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('ConfigTemplatePdusCommand.run')

    template = CHandleRegistry.Instance().Find(StmTemplateConfig)
    if not template or not template.IsTypeOf('StmTemplateConfig'):
        plLogger.LogError('Input StmTemplateConfig is not an StmTemplateConfig')
        return False

    # Load the template's contents into a DOM for processing...
    root = etree.fromstring(template.Get('TemplateXml'))

    sb_elements = xml_utils.find_tagged_elements_by_tag_name(root,
                                                             TemplateElementTagNameList,
                                                             'StreamBlock')
    if not sb_elements or len(sb_elements) == 0:
        plLogger.LogError('TemplateElementTagNameList does not refer ' +
                          'to any streamblock elements.')
        return False

    for sb_ele in sb_elements:
        if not process_pdus(PduPropertyList, PduValueList, sb_ele):
            return False

    # Update the StmTemplateConfig object with all the changes made above...
    template.Set('TemplateXml', etree.tostring(root))
    return True


def process_pdus(properties, values, sb_ele):
    '''
        Broken out of run() to support unit testing...
        pdus is a list of property=value pairs
        sb_ele is the StreamBlock element whose FrameConfig attribute is to be modified.
    '''
    plLogger = PLLogger.GetLogger('methodology')
    plLogger.LogDebug('ConfigTemplatePdusCommand.process_pdus')

    if len(properties) != len(values):
        plLogger.LogError('PropertyList and ValueList are not equal in length.')
        return False

    for ref, val in zip(properties, values):
        # We break the reference into its two pieces...
        parts = ref.split('.')
        # We expect the offsetReference to be in the form 'name.element'...
        if len(parts) != 2:
            plLogger.LogError('Property "' + ref + '" is invalid.')
            return False
        # The name attribute of the target PDU...
        pdu_name = parts[0]
        # The target element of the target PDU...
        pdu_ele = parts[1]

        # Get the FrameConfig attribute from the StreamBlock element...
        fc_attr = sb_ele.get('FrameConfig')
        # If the FrameConfig doesn't exist, then there is a problem
        if fc_attr is None or fc_attr == '':
            plLogger.LogError('FrameConfig attribute is missing from template StreamBlock.')
            return False
        # The attribute holds an encoded XML; it should be decoded automatically by the get()...
        fc = etree.fromstring(fc_attr)
        # We find the target element whose text data we want to update...
        target_ele = fc.find('.//pdu[@name="' + pdu_name + '"]//' + pdu_ele)
        # We assume that the element must exist if pdu_name is present...
        if target_ele is None:
            plLogger.LogError('Property "' + ref + '" is missing or wrong.')
            return False
        # update the text data for the target element...
        target_ele.text = val
        # Update the target StreamBlock's FrameConfig (will auto encode for us)...
        sb_ele.set('FrameConfig', etree.tostring(fc))
    return True


def reset():
    return True
