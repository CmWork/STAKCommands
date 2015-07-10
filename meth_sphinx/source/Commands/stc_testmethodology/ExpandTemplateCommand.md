# ExpandTemplateCommand

Expand an XML template across ports

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### TargetTagList: "Target Tag List" (input:string)

List of tags that indicate where in the STC configuration the template will be copied to.  If TargetTagList is empty, the target will be assumed to be Project.

* default - 
### StmTemplateConfigList: "StmTemplateConfig List" (input:handle)

List of StmTemplateConfig objects

* default - 
### SrcTagList: "Source Tag List" (input:string)

List of tags that indicate where in the XML template the config will be copied from

* default - 
### CopiesPerParent: "Number of copies to make per Target Tag object" (input:u32)

Number of copies of the template to make per Target Tag object

* default - 1
