# ConfigTemplateStmPropertyModifierCommand

Add or configure an StmPropertyModifier in the template

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### Repeat: "Repeat Value" (input:u32)

Modifier Repeat Value

* default - 0
### ObjectName: "Object Name" (input:string)

Class name of the object being modified.  If configuring an existing modifier, this can be left empty. 

* default - 
### PropertyName: "Property Name" (input:string)

Name of the property being modified.  If configuring an existing modifier, this can be left empty. 

* default - 
### StmTemplateConfig: "StmTemplateConfig" (input:handle)

StmTemplateConfig

* default - 
### Start: "Start Value" (input:string)

Modifier Starting Value

* default - 
### Step: "Step Value" (input:string)

Modifier Step Value

* default - 
### TargetObjectTagName: "Target Object's Tag Name" (input:string)

Name of the Tag referencing the target object this modifier is being applied to.  If configuring an existing modifier, this can be left empty.

* default - 
### TagName: "Tag Name" (input:string)

Name of the Tag referencing an StmPropertyModifier object to modify in the template.  If an StmPropertyModifier is being created, this is the name that will be used for a tag that references the StmPropertyModifier.

* default - 
### ModifierType: "Modifier Type" (input:u8)

The type of modifier to add or configure.  If a modifier already exists with the given tag but is of different type, it will be changed to use the new type.

* default - RANGE
### Recycle: "Recycle Value" (input:u32)

Modifier Recycle Value

* default - 0
### ValueType: "Value Type" (input:u8)

The type of the value being modified by the StmPropertyModifier.

* default - INT
## UsedIn
* L3 QoS DiffServ

* BGP Route Reflector Test

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* ACL Basic Test

* RFC 2544 Throughput Test

