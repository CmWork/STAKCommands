# ConfigTemplateProtocolCommand

Configures the tagged ProtocolConfigs in the StmTemplateConfig

<font size="2">File Reference: stc_testmethodology.xml</font>

## Properties

### RowDataJsonSchema: "Row Data JSON Schema" (state:string)

JSON schema that will be used to validate the RowData property's value.

* JSON Schema - 

		{
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
		}


### EnableLoadFromFileName: "Enable XML Template File" (input:bool)

Load the XML from a Template File rather than the Template XML string parameter.

* default - true
### TemplateXml: "XML Template String" (input:string)

Template to use as a string

* default - 
### StmTemplateConfig: "StmTemplateConfig" (input:handle)

StmTemplateConfig

* default - 
### TargetTag: "Target Tag List" (input:string)

Name of the tag on the object in the StmTemplateConfig where the protocol XML will be merged into.

* default - 
### TagPrefix: "Tag Prefix" (input:string)

Prefix value prepended to all tags loaded from the TemplateXmlFileName into the StmTemplateConfig.

* default - 
### RowData: "Row Data" (input:string)

Row of data from the input table containing information about the ProtocolConfig

* default - 
### TemplateXmlFileName: "XML Template File" (input:inputFilePath)

Template XML File Location

* default - 
## JSON Sample

<font color="red">MISSING JSON SAMPLE</font>

## UsedIn
* Routing Multi-Protocol

