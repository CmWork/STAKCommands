# IteratorConfigMixParamsCommand

dummy

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### MixJsonSchema: "Mix JSON Schema" (state:string)

JSON schema that will be used to validate the StmTemplateMix JSON contents.

* JSON Schema - 

		{
		  "required": [
		    "components"
		  ], 
		  "type": "object", 
		  "properties": {
		    "components": {
		      "items": {
		        "required": [
		          "weight", 
		          "useStaticValue", 
		          "staticValue", 
		          "baseTemplateFile"
		        ], 
		        "type": "object", 
		        "properties": {
		          "weight": {
		            "type": "number", 
		            "description": "Percent weight of the total load to assign to this component."
		          }, 
		          "staticValue": {
		            "type": "number", 
		            "description": "Static load to assign to this component.  Static load factors into total load."
		          }, 
		          "useStaticValue": {
		            "type": "boolean", 
		            "description": "Flag indicating a static load should be used instead of a weight."
		          }, 
		          "tagPrefix": {
		            "type": "string", 
		            "description": "String that will be prefixed to all tags loaded and used in this template."
		          }, 
		          "appliedValue": {
		            "type": "number", 
		            "description": "Load actually assigned to this component.  Autocalculated, do not set."
		          }, 
		          "baseTemplateFile": {
		            "type": "string", 
		            "description": "Base template file that will be loaded into the StmTemplateConfig.  All modifications in the modifyList will be applied to the contents loaded out of this file."
		          }
		        }
		      }, 
		      "type": "array", 
		      "description": "A list of components that make up the mixture."
		    }
		  }, 
		  "title": "Schema for the MixInfo of the spirent.methodology.IteratorConfigMixParamsCommand."
		}


### StmTemplateMix: "StmTemplateMix" (input:handle)

StmTemplateMix handle

* default - 
### TagData: "tag Data" (input:string)



* default - 
## JSON Sample

<font color="red">MISSING JSON SAMPLE</font>

## UsedIn
* RFC 2544 Throughput Test

