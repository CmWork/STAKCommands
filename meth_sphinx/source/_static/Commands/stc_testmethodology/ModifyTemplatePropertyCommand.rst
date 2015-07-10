# ModifyTemplatePropertyCommand

Modify an XML template across ports

<font size="2">File Reference: stc_testmethodology.xml</font>

## Properties

### PropertyList: "Property List" (input:string)

List of property IDs (ie classname.property) to configure new values for.  Position in this list MUST map to position in the ValueList.

* default - 
### TagNameList: "Tag Name List" (input:string)

Name of the Tag(s) referencing objects to modify in the template

* default - 
### StmTemplateConfig: "StmTemplateConfig" (input:handle)

StmTemplateConfig

* default - 
### ValueList: "Value List" (input:string)

List of values to configure.  Position in this list MUST map to position in the PropertyList.

* default - 
## UsedIn
* L3 QoS DiffServ

* BGP Route Reflector Test

* ITU-T Y.1564 Service Configuration Test

* Widgets Test

* Basic Traffic Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Basic Test

* RFC 2544 Throughput Test

