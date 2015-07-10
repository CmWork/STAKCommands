# AddTemplateObjectCommand

Add a new STC object to the template

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### StmTemplateConfig: "StmTemplateConfig" (input:handle)

StmTemplateConfig

* default - 
### TagName: "Tag Name" (input:string)

Name of a new tag to create and attach to the added objects

* default - 
### PropertyList: "Property List" (input:string)

List of property IDs on the newly created object to configure new values for.  Position in this list MUST map to position in the ValueList.

* default - 
### ClassName: "Class Name" (input:string)

Class name of the object

* default - 
### ValueList: "Value List" (input:string)

List of values to configure on the newly created object.  Position in this list MUST map to position in the PropertyList.

* default - 
### ParentTagName: "Parent Tag Name" (input:string)

Name of the tag from which parent objects will be found to add new objects to under

* default - 
