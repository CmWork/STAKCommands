# CreateRouteMixCommand

Command for creating mixtures of route counts among route objects on tagged router config objects.

<font size="2">File Reference: stc_methodology_routing.xml</font>

<text>Properties</text>

### MixInfoJsonSchema: "Table Data JSON Schema" (state:string)

JSON schema that will be used to validate the MixInfo property's value.

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
		          "baseTemplateFile"
		        ], 
		        "type": "object", 
		        "properties": {
		          "postExpandModify": {
		            "items": {
		              "type": "object", 
		              "properties": {
		                "bllWizardExpand": {
		                  "type": "object", 
		                  "description": "Process route wizard params, invoke BLL command, tag resulting routes.", 
		                  "properties": {
		                    "targetTagList": {
		                      "items": {
		                        "type": "string"
		                      }, 
		                      "type": "array", 
		                      "description": "List of tag names representing routers that will have routes applied onto them."
		                    }, 
		                    "srcObjectTagName": {
		                      "type": "string", 
		                      "description": "Tag name that represents the loaded wizard params object."
		                    }, 
		                    "commandName": {
		                      "type": "string", 
		                      "description": "Name of command that will be invoked with the targetTagList, srcObjectTagName, and createdRoutesTagName."
		                    }, 
		                    "createdRoutesTagName": {
		                      "type": "string", 
		                      "description": "Tag name that will be affected upon the routes that are created by the BLL wizard."
		                    }
		                  }
		                }
		              }
		            }, 
		            "type": "array", 
		            "description": "A list of operations that will be carried out on datamodel objects after the template is expanded."
		          }, 
		          "modifyList": {
		            "items": {
		              "type": "object"
		            }, 
		            "type": "array", 
		            "description": "A list of operations that will be carried out on the template.  See the schema defined in the spirent.methodology.CreateTemplateConfigCommand."
		          }, 
		          "tagPrefix": {
		            "type": "string", 
		            "description": "String that will be prefixed to all tags loaded and used in this template."
		          }, 
		          "weight": {
		            "type": "string", 
		            "description": "The weight of this component upon network counts."
		          }, 
		          "baseTemplateFile": {
		            "type": "string", 
		            "description": "Base template file that will be loaded into the StmTemplateConfig.  All modifications in the modifyList will be applied to the contents loaded out of this file."
		          }
		        }
		      }, 
		      "type": "array", 
		      "description": "A list of components that make up the mixture."
		    }, 
		    "routeCount": {
		      "type": "number", 
		      "description": "Total number of routes for all components in this mix"
		    }
		  }, 
		  "title": "Schema for the MixInfo of the spirent.methodology.CreateRouteMixCommand."
		}


### MixTagName: "Mix Container Tag Name" (input:string)

Name to use when tagging the output StmTemplateMix.  If left blank, StmTemplateMix will not be tagged.

* default - 
### MixInfo: "Mix Info" (input:string)

JSON string representation of the mix (including table data)

* default - 
### TargetObjectList: "Target Object List" (input:handle)

List of StmProtocolMix, StmTemplateConfig, EmulatedDevice, or RouterConfig objects, that we will expand RouteConfig objects under

* default - 
### GroupCommandTagInfo: "Group Command Tag Info" (state:string)

JSON structure containing the names of the tags used to refer to commands in this group.

* default - 
### AutoExpandTemplateMix: "Automatically expand templates in the mix" (input:bool)

Automatically expand templates.

* default - true
### TargetObjectTagList: "Target Object Tag List" (input:string)

List of tag names, which tag StmProtocolMix, StmTemplateConfig, EmulatedDevice, or RouterConfig objects, that we will expand RouteConfig objects under.

* default - 
## JSON Sample

<font color="red">MISSING JSON SAMPLE</font>

