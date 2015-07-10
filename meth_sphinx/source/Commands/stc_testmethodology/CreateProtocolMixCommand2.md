# CreateProtocolMixCommand2

Command for creating mixtures of protocols on an Emulated Device block.

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### TagPrefixList: "Tag Prefix" (input:string)

Tag name representing the port group on which devices and protocols should be expanded on.

* default - 
### MixInfoJsonSchema: "Table Data JSON Schema" (state:string)

JSON schema that will be used to validate the TableData property's value.

* JSON Schema - 

		{
		  "required": [
		    "deviceCount", 
		    "components"
		  ], 
		  "type": "object", 
		  "properties": {
		    "deviceCount": {
		      "type": "number", 
		      "description": "Total Device Count for StmTemplateMix distribution."
		    }, 
		    "components": {
		      "items": {
		        "required": [
		          "weight", 
		          "devicesPerBlock", 
		          "baseTemplateFile"
		        ], 
		        "type": "object", 
		        "properties": {
		          "weight": {
		            "type": "string", 
		            "description": "If value is followed by %, this is the percent weight of the total deviceCount to assign to this component. Otherwise, this becomes a static deviceCount value."
		          }, 
		          "tagPrefix": {
		            "type": "string", 
		            "description": "String that will be prefixed to all tags loaded and used in this template."
		          }, 
		          "appliedValue": {
		            "type": "number", 
		            "description": "Load actually assigned to this component.  Autocalculated, do not set."
		          }, 
		          "modifyList": {
		            "items": {
		              "type": "object", 
		              "properties": {
		                "mergeList": {
		                  "items": {
		                    "type": "object"
		                  }, 
		                  "type": "array", 
		                  "description": "A list of merge operations where a XML file will be used as a source of XML to merge into the XML contained in the StmTemplateConfig."
		                }
		              }
		            }, 
		            "type": "array", 
		            "description": "A list of operations that will be carried out on the template.  See the schema defined in the spirent.methodology.CreateTemplateConfigCommand."
		          }, 
		          "baseTemplateFile": {
		            "type": "string", 
		            "description": "Base template file that will be loaded into the StmTemplateConfig.  All modifications in the modifyList will be applied to the contents loaded out of this file."
		          }, 
		          "devicesPerBlock": {
		            "type": "number", 
		            "description": "Number that indicates how many device will be assigned per device block.  If 0, devicesPerBlock indicates all deviceCount is assigned to one block. If 1, devicesPerBlock = # of device blocks with a device count of 1. If devicesPerBlock > device count of component (after weight is applied), all devices go into one block.  Otherwise, blocks are greedily created until we run out of device count (ie. deviceCount = 17, devicesPerBlock = 5, blocks created with 5, 5, 5, 2 devices)."
		          }
		        }
		      }, 
		      "type": "array", 
		      "description": "A list of components that make up the mixture."
		    }
		  }, 
		  "title": "Schema for the MixInfo of the spirent.methodology.CreateProtocolMixCommand."
		}


### MixTagName: "Mix Container Tag Name" (input:string)

Name to use when tagging the output StmProtocolMix.  If left blank, StmProtocolMix will not be tagged.

* default - 
### PortGroupTagList: "Port Group Tag" (input:string)

Tag name representing the port group on which devices and protocols should be expanded on.

* default - 
### MixInfo: "Mix Info" (input:string)

JSON string representation of the mix (including table data)

* default - 
### GroupCommandTagInfo: "Group Command Tag Info" (state:string)

JSON structure containing the names of the tags used to refer to commands in this group.

* default - 
### AutoExpandTemplateMix: "Automatically expand templates in the mix" (input:bool)

Automatically expand templates.

* default - true
## JSON Sample

<font color="red">MISSING JSON SAMPLE</font>

