# LoadTemplateCommand

Load an XML template into an StmTemplateConfig object

<font size="2">File Reference: stc_testmethodology.xml</font>

## Properties

### TargetTagList: "Target Tag List" (input:string)

List of tags where the Source Tags will be appended.

* default - 
### EnableLoadFromFileName: "Enable XML Template File" (input:bool)

Load the XML from a Template File rather than the Template XML string parameter.

* default - true
### AutoExpandTemplate: "Automatically Expand Template" (input:bool)

Expand template into EmulatedDevices, Streamblocks, etc.

* default - true
### TemplateXml: "XML Template String" (input:string)

Template to use as a string

* default - 
### StmTemplateConfig: "XML container object (StmTemplateConfig)" (output:handle)

StmTemplateConfig container object

* default - 
### TagPrefix: "Tag Prefix" (input:string)

Prefix value prepended to all tags loaded by configuration

* default - 
### TemplateXmlFileName: "XML Template File" (input:inputFilePath)

Template XML File Location

* default - 
### StmTemplateMix: "Parent StmTemplateMix object" (input:handle)

Handle of an StmTemplateMix object to use for the parent of the created StmTemplateConfig.

* default - 
### CopiesPerParent: "Number of copies to make per Target Tag object" (input:u32)

Number of copies of the template to make per Target Tag object

* default - 1
## UsedIn
* L3 QoS DiffServ

* BGP Route Reflector Test

* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* Widgets Test

* Basic Traffic Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* ACL Basic Test

* RFC 2544 Throughput Test

