# MergeTemplateCommand

Merges XML from a source string or file into the StmTemplateConfig container using source and target tags.

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### TargetTagList: "Target Tag List" (input:string)

List of tags in the StmTemplateConfig's TemplateXml string where the Source Tag List's tagged elements will be inserted.

* default - 
### EnableLoadFromFileName: "Enable XML Template File" (input:bool)

Load the XML from a Template File rather than the Template XML string parameter.

* default - true
### TemplateXml: "XML Template String" (input:string)

String XML that will serve as a source

* default - 
### StmTemplateConfig: "StmTemplateConfig (from LoadTemplateCommand)" (input:handle)

StmTemplateConfig container object passed in from the LoadTemplateCommand

* default - 
### TagPrefix: "Tag Prefix" (input:string)

Prefix value prepended to all merged tags loaded in the source XML

* default - 
### TemplateXmlFileName: "XML Template File" (input:inputFilePath)

Template XML File Location that will serve as a source

* default - 
### SrcTagList: "Source Tag List" (input:string)

List of tags from the XML Template String or File whose elements will be merged into the TemplateXml contained in the StmTemplateConfig

* default - 
