# ModifyHandleListCommand

Modify a property of a BLL command that contains a list of handles

<font size="2">File Reference: stc_testmethodology.xml</font>

## Properties

### OverwriteProperty: "Overwrite Property" (input:bool)

If set to true, will overwrite the property to modify.  If false, command will append.

* default - true
### PropertyName: "Property To Modify" (input:string)

The property in the target BLL command that will have its contents modified.

* default - 
### BllCommandTagName: "Tag that identifies target BLL Command" (input:string)

Name of the tag that the target BLL command will have a UserTag relation to.

* default - 
### TagList: "Tag List" (input:string)

List of tags that will be expanded into BLL objects, then passed in to the command.  If the command already has handles, these handles will be appended to its list.

* default - 
## UsedIn
* L3 QoS DiffServ

* BGP Route Reflector Test

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* Widgets Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ITU-T Y.1564 Microburst Test

