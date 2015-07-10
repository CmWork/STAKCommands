# ConfigTemplatePdusCommand

This command will configure PDUs in the Streamblock template's FrameConfig that itself is found in the StmTemplateConfig, using the information from PduInfo property.

<font size="2">File Reference: stc_testmethodology.xml</font>

## Properties

### StmTemplateConfig: "StmTemplateConfig" (input:handle)

StmTemplateConfig handle

* default - 
### PduValueList: "PDU Information Value List" (input:string)

List of values to modify PDU information within streamblocks' FrameConfig properties.

* default - 
### TemplateElementTagNameList: "Template Element Tag Name List" (input:string)

List of tag names that refer to the targeted stream block (XML elements) in the template.

* default - 
### PduPropertyList: "PDU Information Property List" (input:string)

List of properties to modify PDU information within streamblocks' FrameConfig properties.

* default - 
