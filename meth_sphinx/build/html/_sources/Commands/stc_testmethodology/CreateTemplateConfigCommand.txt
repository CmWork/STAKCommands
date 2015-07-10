# CreateTemplateConfigCommand

Create an StmTemplateConfig by load an XML template and modifying it.

<img src='somesource' />

<font size="2">File Reference: stc_testmethodology.xml</font>

## Properties

### TargetTagList: "Target Tag List" (input:string)

List of tags that indicate where in the STC configuration the template will be copied to.  If TargetTagList is empty, the target will be assumed to be Project.

* default - 
### InputJsonSchema: "Input JSON Schema" (state:string)

JSON schema that will be used to validate the InputJson property's value.

* JSON Schema - 

		{
		  "required": [
		    "baseTemplateFile"
		  ], 
		  "type": "object", 
		  "properties": {
		    "modifyList": {
		      "items": {
		        "type": "object", 
		        "properties": {
		          "stmPropertyModifierList": {
		            "items": {
		              "type": "object", 
		              "properties": {
		                "items": {
		                  "className": {
		                    "type": "string", 
		                    "description": "Class name of the object type that properties will be modified on."
		                  }, 
		                  "propertyName": {
		                    "type": "string", 
		                    "description": "Name of the property that an StmPropertyModifier is being attached onto."
		                  }, 
		                  "parentTagName": {
		                    "type": "string", 
		                    "description": "Name of the tag that tags the object that an StmPropertyModifier will be added or configured on."
		                  }, 
		                  "tagName": {
		                    "type": "string", 
		                    "description": "Name of the tag that tags objects of type className."
		                  }, 
		                  "propertyValueList": {
		                    "type": "object", 
		                    "description": "List of property-value pairs that will be modified.  This list should contain property names that exist in the StmPropertyModifier's ModifierInfo."
		                  }
		                }
		              }
		            }, 
		            "required": [
		              "className", 
		              "tagName", 
		              "propertyValueList"
		            ], 
		            "type": "array", 
		            "description": "A list of config StmPropertyModifier operations to add or configure StmPropertyModifiers in the StmTemplateConfig."
		          }, 
		          "propertyValueList": {
		            "items": {
		              "type": "object", 
		              "properties": {
		                "className": {
		                  "type": "string", 
		                  "description": "Class name of the object type that properties will be modified on."
		                }, 
		                "tagName": {
		                  "type": "string", 
		                  "description": "Name of the tag that tags objects of type className."
		                }, 
		                "propertyValueList": {
		                  "type": "object", 
		                  "description": "List of property-value pairs that will be modified."
		                }
		              }
		            }, 
		            "required": [
		              "className", 
		              "tagName", 
		              "propertyValueList"
		            ], 
		            "type": "array", 
		            "description": "A list of modify template operations to change the values of properties on tagged objects."
		          }, 
		          "relationList": {
		            "items": {
		              "type": "object", 
		              "properties": {
		                "relationType": {
		                  "type": "string", 
		                  "description": "The type of relation to add or remove, ie StackedOnEndpoint or UsesIf."
		                }, 
		                "sourceTag": {
		                  "type": "string", 
		                  "description": "Name of the tag that tags an object that is the source of the relation."
		                }, 
		                "removeRelation": {
		                  "type": "boolean", 
		                  "description": "A flag indicating if the relation should be removed if found."
		                }, 
		                "targetTag": {
		                  "type": "string", 
		                  "description": "Name of the tag that tags an object that is the target of the relation."
		                }
		              }
		            }, 
		            "required": [
		              "relationType", 
		              "targetTagList"
		            ], 
		            "type": "array", 
		            "description": "A list of configure relation operations to add or remove relations between elements in the StmTemplateConfig."
		          }, 
		          "pduModifierList": {
		            "items": {
		              "type": "object", 
		              "properties": {
		                "templateElementTagName": {
		                  "type": "string", 
		                  "description": "Name of the tag that tags StreamBlock objects."
		                }, 
		                "value": {
		                  "type": "string", 
		                  "description": "String value for the PDU property."
		                }, 
		                "offsetReference": {
		                  "type": "string", 
		                  "description": "String in the form of . that refers to a particular field in a particular PDU that will be modified."
		                }
		              }
		            }, 
		            "required": [
		              "offsetReference"
		            ], 
		            "type": "array", 
		            "description": "A list of PDU modification operations to change values in a StreamBlock's FrameConfig."
		          }, 
		          "mergeList": {
		            "items": {
		              "type": "object", 
		              "properties": {
		                "stmPropertyModifierList": {
		                  "items": {
		                    "type": "object", 
		                    "properties": {
		                      "items": {
		                        "className": {
		                          "type": "string", 
		                          "description": "Class name of the object type that properties will be modified on."
		                        }, 
		                        "propertyName": {
		                          "type": "string", 
		                          "description": "Name of the property that an StmPropertyModifier is being attached onto."
		                        }, 
		                        "parentTagName": {
		                          "type": "string", 
		                          "description": "Name of the tag that tags the object that an StmPropertyModifier will be added or configured on."
		                        }, 
		                        "tagName": {
		                          "type": "string", 
		                          "description": "Name of the tag that tags objects of type className."
		                        }, 
		                        "propertyValueList": {
		                          "type": "object", 
		                          "description": "List of property-value pairs that will be modified.  This list should contain property names that exist in the StmPropertyModifier's ModifierInfo."
		                        }
		                      }
		                    }
		                  }, 
		                  "required": [
		                    "className", 
		                    "tagName", 
		                    "propertyValueList"
		                  ], 
		                  "type": "array", 
		                  "description": "A list of config StmPropertyModifier operations to add or configure StmPropertyModifiers in the StmTemplateConfig."
		                }, 
		                "propertyValueList": {
		                  "items": {
		                    "type": "object", 
		                    "properties": {
		                      "className": {
		                        "type": "string", 
		                        "description": "Class name of the object type that properties will be modified on."
		                      }, 
		                      "tagName": {
		                        "type": "string", 
		                        "description": "Name of the tag that tags objects of type className."
		                      }, 
		                      "propertyValueList": {
		                        "type": "object", 
		                        "description": "List of property-value pairs that will be modified."
		                      }
		                    }
		                  }, 
		                  "required": [
		                    "className", 
		                    "tagName", 
		                    "propertyValueList"
		                  ], 
		                  "type": "array", 
		                  "description": "A list of modify template operations to change the values of properties on tagged objects."
		                }, 
		                "mergeSourceTag": {
		                  "type": "string", 
		                  "description": "The name of the tag in the XML file from which tagged elements will be merged into the StmTemplateConfig."
		                }, 
		                "mergeSourceTemplateFile": {
		                  "type": "string", 
		                  "description": "The path to the source XML file."
		                }, 
		                "mergeTagPrefix": {
		                  "type": "string", 
		                  "description": "A string that will be prefixed to the tags that are merged from the source file to the StmTemplateConfig."
		                }, 
		                "mergeTargetTag": {
		                  "type": "string", 
		                  "description": "The name of the tag in the StmTemplateConfig where elements from the XML file will be merged into."
		                }
		              }
		            }, 
		            "required": [
		              "mergeSourceTag", 
		              "mergeSourceTemplateFile", 
		              "mergeTargetTag"
		            ], 
		            "type": "array", 
		            "description": "A list of merge operations where a XML file will be used as a source of XML to merge into the XML contained in the StmTemplateConfig."
		          }, 
		          "addObjectList": {
		            "items": {
		              "type": "object", 
		              "properties": {
		                "className": {
		                  "type": "string", 
		                  "description": "Class name of the object type that will be added."
		                }, 
		                "parentTagName": {
		                  "type": "string", 
		                  "description": "Name of the tag that tags parent objects for type className."
		                }, 
		                "tagName": {
		                  "type": "string", 
		                  "description": "Name of the tag that tags newly created objects of type className."
		                }, 
		                "propertyValueList": {
		                  "type": "object", 
		                  "description": "List of property-value pairs that will be modified."
		                }
		              }
		            }, 
		            "required": [
		              "className", 
		              "parentTagName", 
		              "tagName"
		            ], 
		            "type": "array", 
		            "description": "A list of objects to add to a template."
		          }
		        }
		      }, 
		      "type": "array", 
		      "description": "A list of operations that will be carried out on the template."
		    }, 
		    "tagPrefix": {
		      "type": "string", 
		      "description": "String that will be prefixed to all tags loaded and used in this template."
		    }, 
		    "baseTemplateFile": {
		      "type": "string", 
		      "description": "Base template file that will be loaded into the StmTemplateConfig.  All modifications in the modifyList will be applied to the contents loaded out of this file."
		    }
		  }, 
		  "title": "Schema for InputJson of the spirent.methodology.CreateTemplateConfigCommand."
		}


### AutoExpandTemplate: "Automatically Expand Template" (input:bool)

Expand template into EmulatedDevices, Streamblocks, etc.

* default - true
### StmTemplateMix: "Parent StmTemplateMix object" (input:handle)

Handle of an StmTemplateMix object to use for the parent of the created StmTemplateConfig.

* default - 
### StmTemplateConfig: "XML container object (StmTemplateConfig)" (output:handle)

StmTemplateConfig container object

* default - 
### InputJson: "JSON Input" (input:string)

JSON string representation of parameters to load and modify template(s) into the StmTemplateConfig.

* default - {"baseTemplateFile": "IPv4_NoVlan.xml"}
### SrcTagList: "Source Tag List" (input:string)

List of tags that indicate where in the XML template the config will be expanded from

* default - 
### CopiesPerParent: "Number of copies to make per Target Tag object" (input:u32)

Number of copies of the template to make per Target Tag object

* default - 1
## JSON Sample

		{
		  "here": "there"
		}


## UsedIn
* RFC 2544 Throughput Test

