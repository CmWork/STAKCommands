# InsertTemplateIfCommand

Adds an interface to the template and stacks it between an ipv4 interface and an eth interface

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### StmTemplateConfig: "StmTemplateConfig" (input:handle)

StmTemplateConfig container object. The value shall be passed in from the parent Load Template Command.

* default - 
### TagName: "Tag Name for Inserted Interface" (input:string)

Tag name to be set on the newly created interface.

* default - ttVlanIf
### UpperIfTagNameList: "Upper Interface Tag Name List" (input:string)

List of tag names of upper interfaces.

* default - 
### LowerIfTagName: "Lower Interface Tag Name" (input:string)

Tag name of the lower interface.

* default - ttEthIIIf
### PropertyList: "Property List" (input:string)

List of property IDs on the newly created interface to configure values for. Position in this list must map to position in the Value List.

* default - 
### IfClassName: "Interface Class Name" (input:string)

Type of interface to be created. For example VlanIf.

* default - VlanIf
### TagPrefix: "Tag Prefix" (input:string)

Prefix value prepended to all tag names, including Parent Tag Name, Lower Interface Tag Name, Upper Interface Tag Name and Tag Name for Inserted Interface.

* default - 
### ValueList: "Value List" (input:string)

List of values to configure on the newly created interface. Position in this list must map to position in the Property List.

* default - 
### ParentTagName: "Parent Tag Name" (input:string)

Name of the tag from which the parent object will be found to add the new interface under.

* default - ttEmulatedDevice
