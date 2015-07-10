# CreateTrafficMix2Command

Command for creating mixtures of traffic between tagged end points.

<font size="2">File Reference: stc_methodology_traffic.xml</font>

<text>Properties</text>

### MixInfoJsonSchema: "Table Data JSON Schema" (state:string)

JSON schema that will be used to validate the MixInfo property's value.

* JSON Schema - 

		{
		  "required": [
		    "load", 
		    "loadUnits", 
		    "components"
		  ], 
		  "type": "object", 
		  "properties": {
		    "load": {
		      "type": "number", 
		      "description": "Traffic mix total load in appropriate units."
		    }, 
		    "loadUnits": {
		      "enum": [
		        "PERCENT_LINE_RATE", 
		        "FRAMES_PER_SECOND", 
		        "INTER_BURST_GAP", 
		        "BITS_PER_SECOND", 
		        "KILOBITS_PER_SECOND", 
		        "MEGABITS_PER_SECOND"
		      ], 
		      "description": "Traffic load units."
		    }, 
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
		          "postExpandModify": {
		            "items": {
		              "required": [
		                "streamBlockExpand"
		              ], 
		              "type": "object", 
		              "properties": {
		                "streamBlockExpand": {
		                  "required": [
		                    "endpointMappingList"
		                  ], 
		                  "type": "object", 
		                  "description": "Process project-level streamblocks and expand onto ports.", 
		                  "properties": {
		                    "endpointMappingList": {
		                      "items": {
		                        "additionalProperties": false, 
		                        "required": [
		                          "srcBindingTag", 
		                          "dstBindingTag"
		                        ], 
		                        "type": "object", 
		                        "properties": {
		                          "dstBindingTag": {
		                            "type": "string", 
		                            "description": "Name of the tag for streamblock destination binding endpoints."
		                          }, 
		                          "srcBindingTag": {
		                            "type": "string", 
		                            "description": "Name of the tag for streamblock source binding endpoints."
		                          }
		                        }
		                      }, 
		                      "type": "array", 
		                      "description": "List of tag names representing endpoints that will be mapped on the port-level streamblocks."
		                    }
		                  }
		                }
		              }
		            }, 
		            "type": "array", 
		            "description": "A list of operations that will be carried out on datamodel objects after the template is expanded."
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
		          "modifyList": {
		            "items": {
		              "type": "object"
		            }, 
		            "type": "array", 
		            "description": "A list of operations that will be carried out on the template.  See the schema defined in the spirent.methodology.CreateTemplateConfigCommand."
		          }, 
		          "baseTemplateFile": {
		            "type": "string", 
		            "description": "Base template file that will be loaded into the StmTemplateConfig.  All modifications in the modifyList will be applied to the contents loaded out of this file."
		          }, 
		          "expand": {
		            "required": [
		              "targetTagList"
		            ], 
		            "type": "object", 
		            "properties": {
		              "targetTagList": {
		                "items": {
		                  "type": "string"
		                }, 
		                "type": "array", 
		                "description": "List of Target Tags passed to expand"
		              }, 
		              "srcTagList": {
		                "items": {
		                  "type": "string"
		                }, 
		                "type": "array", 
		                "description": "List of Source Tags passed to expand"
		              }, 
		              "copiesPerParent": {
		                "type": "number", 
		                "description": "streamblocks to make per parent"
		              }
		            }
		          }
		        }
		      }, 
		      "type": "array", 
		      "description": "A list of components that make up the mixture."
		    }
		  }, 
		  "title": "Schema for the MixInfo of the spirent.methodology.CreateTrafficMixCommand."
		}


### GroupCommandTagInfo: "Group Command Tag Info" (state:string)

JSON structure containing the names of the tags used to refer to commands in this group.

* default - 
### MixInfo: "Mix Info" (input:string)

JSON string representation of the mix (including table data)

* default - 
### AutoExpandTemplateMix: "Automatically expand templates in the mix" (input:bool)

Automatically expand templates.

* default - true
### MixTagName: "Mix Container Tag Name" (input:string)

Name to use when tagging the output StmProtocolMix.  If left blank, StmTemplateMix will not be tagged.

* default - 
## JSON Sample

<font color="red">MISSING JSON SAMPLE</font>

## UsedIn
* RFC 2544 Throughput Test

