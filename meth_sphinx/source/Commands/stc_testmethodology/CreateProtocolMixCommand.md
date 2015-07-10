# CreateProtocolMixCommand

Command for creating mixtures of protocols on an Emulated Device block.

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### TableDataJsonSchema: "Table Data JSON Schema" (state:string)

JSON schema that will be used to validate the TableData property's value.

* JSON Schema - 

		{
		  "items": {
		    "required": [
		      "weight", 
		      "baseTemplateFile", 
		      "protocolTemplateFile", 
		      "deviceTag", 
		      "useBlock"
		    ], 
		    "type": "object", 
		    "properties": {
		      "weight": {
		        "type": "number"
		      }, 
		      "useBlock": {
		        "type": "boolean"
		      }, 
		      "staticDeviceCount": {
		        "type": "number"
		      }, 
		      "useStaticDeviceCount": {
		        "type": "boolean"
		      }, 
		      "deviceTag": {
		        "type": "string"
		      }, 
		      "interfaceList": {
		        "items": {
		          "type": "object", 
		          "properties": {
		            "stmPropertyModifierList": {
		              "items": {
		                "className": {
		                  "type": "string"
		                }, 
		                "propertyName": {
		                  "type": "string"
		                }, 
		                "parentTagName": {
		                  "type": "string"
		                }, 
		                "tagName": {
		                  "type": "string"
		                }, 
		                "propertyValueList": {
		                  "type": "object"
		                }
		              }, 
		              "required": [
		                "className", 
		                "tagName", 
		                "propertyValueList"
		              ], 
		              "type": "array"
		            }, 
		            "propertyValueList": {
		              "items": {
		                "type": "object", 
		                "properties": {
		                  "className": {
		                    "type": "string"
		                  }, 
		                  "tagName": {
		                    "type": "string"
		                  }, 
		                  "propertyValueList": {
		                    "type": "object"
		                  }
		                }
		              }, 
		              "type": "array"
		            }
		          }
		        }, 
		        "type": "array"
		      }, 
		      "baseTemplateFile": {
		        "type": "string"
		      }, 
		      "protocolList": {
		        "items": {
		          "required": [
		            "protocolSrcTag"
		          ], 
		          "type": "object", 
		          "properties": {
		            "protocolSrcTag": {
		              "type": "string"
		            }, 
		            "stmPropertyModifierList": {
		              "items": {
		                "className": {
		                  "type": "string"
		                }, 
		                "propertyName": {
		                  "type": "string"
		                }, 
		                "parentTagName": {
		                  "type": "string"
		                }, 
		                "tagName": {
		                  "type": "string"
		                }, 
		                "propertyValueList": {
		                  "type": "object"
		                }
		              }, 
		              "required": [
		                "className", 
		                "tagName", 
		                "propertyValueList"
		              ], 
		              "type": "array"
		            }, 
		            "propertyValueList": {
		              "items": {
		                "type": "object", 
		                "properties": {
		                  "className": {
		                    "type": "string"
		                  }, 
		                  "tagName": {
		                    "type": "string"
		                  }, 
		                  "propertyValueList": {
		                    "type": "object"
		                  }
		                }
		              }, 
		              "type": "array"
		            }
		          }
		        }, 
		        "type": "array"
		      }, 
		      "protocolTemplateFile": {
		        "type": "string"
		      }
		    }
		  }, 
		  "type": "array"
		}


### TagPrefixList: "Tag Prefix" (input:string)

Tag name representing the port group on which devices and protocols should be expanded on.

* default - 
### MixTagName: "Mix Container Tag Name" (input:string)

Name to use when tagging the output StmProtocolMix.  If left blank, StmProtocolMix will not be tagged.

* default - 
### DeviceCount: "Total Device Count" (input:u64)

Total number of devices to divide among the protocols in the mix

* default - 1
### PortGroupTagList: "Port Group Tag" (input:string)

Tag name representing the port group on which devices and protocols should be expanded on.

* default - 
### GroupCommandTagInfo: "Group Command Tag Info" (state:string)

JSON structure containing the names of the tags used to refer to commands in this group.

* default - 
### TableData: "Table Data" (input:string)

JSON string representation of the input table

* default - 
### AutoExpandTemplateMix: "Automatically expand templates in the mix" (input:bool)

Automatically expand templates.

* default - true
## JSON Sample

<font color="red">MISSING JSON SAMPLE</font>

## UsedIn
* Routing Multi-Protocol

