# ConfigTemplateNetworkIfCommand

Configures the tagged Interfaces in the StmTemplateConfig

<font size="2">File Reference: stc_testmethodology.xml</font>

## Properties

### RowData: "Row Data" (input:string)

Row of data from the input table containing information about the Network Interface

* default - 
### RowDataJsonSchema: "Row Data JSON Schema" (state:string)

JSON schema that will be used to validate the RowData property's value.

* JSON Schema - 

		{
		  "items": {
		    "type": "object", 
		    "properties": {
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
		      "insertInterface": {
		        "type": "object", 
		        "properties": {
		          "className": {
		            "type": "string"
		          }, 
		          "upperIfTag": {
		            "type": "array"
		          }, 
		          "lowerIfTag": {
		            "type": "string"
		          }, 
		          "parentTagName": {
		            "type": "string"
		          }, 
		          "tagName": {
		            "type": "string"
		          }
		        }
		      }
		    }
		  }, 
		  "type": "array"
		}


### StmTemplateConfig: "StmTemplateConfig" (input:handle)

StmTemplateConfig

* default - 
### TagPrefix: "Tag Prefix" (input:string)

Prefix value prepended to all tags referenced in the StmTemplateConfig.

* default - 
## JSON Sample

<font color="red">MISSING JSON SAMPLE</font>

## UsedIn
* Routing Multi-Protocol

