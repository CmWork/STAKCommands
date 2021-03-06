# AllocateTrafficMixLoadCommand

Takes the load of a given mix and distributes it across the components of the mix, according to the JSON information found in the StmTemplateMix object for the traffic mix. Multiple StmTemplateMix objects can be processed by this command, but each will be processed independtly as though it were the only mix to be handled by this command.<BR><BR>This command is typically called internally by the CreateTrafficMixCommand (when auto expand is enabled), or externally in the sequencer when changing of loads during iterative test loops is necessary.

<h2>- Properties</h2>

<h3>StmTrafficMix (input:handle)<br><font size=2>"Traffic Mix"</font></h3>

Handle to an StmTemplate Mix container object that contains the traffic mix information. This value can be empty, in which case a tag name must be supplied to the TrafficMixTagName property.

* default: <font color=#cc8888>(empty)</font>

<h3>TrafficMixTagName (input:string)<br><font size=2>"Tag name for Traffic Mix"</font></h3>

Name of the tag that is attached to one or more StmTemplateMix's. Every StmTemplateMix object associated with the tag is expanded. This property can be empty, in which case a handle to an StmTemplateMix object must be provided in the StmTemplateMix property.

* default: <font color=#cc8888>(empty string)</font>

<h3>Load (input:double)<br><font size=2>"Load"</font></h3>

The total traffic load distributed across each expanded traffic mix. The value of this property is strictly a numerical value. The units that this value is to be interpreted with is found in the LoadUnit property.

* default: 10.0

<h3>LoadUnit (input:u8)<br><font size=2>"Load Unit"</font></h3>

The units to be applied to the Load property.

* default: PERCENT_LINE_RATE

		StreamBlock.EnumLoadUnit


<h3>MixInfoJsonSchema (state:string)<br><font size=2>"Table Data JSON Schema"</font></h3>

JSON schema that will be used to validate the mix information in JSON form found in the StmTemplateMix object.



<h3><a id="schema.for.AllocateTrafficMixLoadCommand.MixInfoJsonSchema.h3link" href="JavaScript:;" onclick="toggle_visibility('schema.for.AllocateTrafficMixLoadCommand.MixInfoJsonSchema');">JSON Schema [+]</a></h3>

<div class="section" style="display:none;" id="schema.for.AllocateTrafficMixLoadCommand.MixInfoJsonSchema"><pre><code class="hljs json">		{
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
		          "baseTemplateFile"
		        ], 
		        "type": "object", 
		        "properties": {
		          "weight": {
		            "type": "string", 
		            "description": "Percent weight of the total load to assign to this component."
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
		                    "endpointMapping"
		                  ], 
		                  "type": "object", 
		                  "description": "Process project-level streamblocks and expand onto ports.", 
		                  "properties": {
		                    "endpointMapping": {
		                      "additionalProperties": false, 
		                      "required": [
		                        "srcBindingTagList"
		                      ], 
		                      "type": "object", 
		                      "description": "Description of end points that will be mapped on the port-level streamblocks.", 
		                      "properties": {
		                        "bidirectional": {
		                          "type": "boolean", 
		                          "description": "True if a streamblock is to be created for both directions (flipping the src and dst for the second streamblock), false if only one direction, must be false for MESH configuration."
		                        }, 
		                        "srcBindingClassList": {
		                          "items": {
		                            "type": "string", 
		                            "description": "The classname that we will search the srcBindingTagList objects for."
		                          }, 
		                          "type": "array"
		                        }, 
		                        "dstBindingTagList": {
		                          "items": {
		                            "type": "string", 
		                            "description": "List of tag names for streamblock destination binding endpoints, not used in MESH configuration."
		                          }, 
		                          "type": "array"
		                        }, 
		                        "srcBindingTagList": {
		                          "items": {
		                            "type": "string", 
		                            "description": "List of tag names for streamblock source binding endpoints."
		                          }, 
		                          "type": "array"
		                        }, 
		                        "dstBindingClassList": {
		                          "items": {
		                            "type": "string", 
		                            "description": "The classname that we will search the dstBindingTagList objects for."
		                          }, 
		                          "type": "array"
		                        }
		                      }
		                    }
		                  }
		                }
		              }
		            }, 
		            "type": "array", 
		            "description": "A list of operations that will be carried out on datamodel objects after the template is expanded."
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
		  "title": "Schema for the MixInfo of the spirent.methodology.traffic.AllocateTrafficMixLoadCommand."
		}


</code></pre></div><font color="red">MISSING JSON SAMPLE</font>

<h2>- UsedIn</h2>
* RFC 2544 Throughput Test


<script type="text/javascript">
<!--
    function toggle_visibility(id) {
       var e = document.getElementById(id);
       var caption = document.getElementById(id + '.h3link');
       var text = caption.innerHTML
       if(e.style.display == 'block')
       {
          e.style.display = 'none';
          caption.innerHTML = text.replace('[-]', '[+]');
       }
       else
       {
          e.style.display = 'block';
          caption.innerHTML = text.replace('[+]', '[-]');
       }
    }
//!-->
</script># CreateTrafficMixCommand

<h3>Extends spirent.methodology.CreateTemplateMixCommand.</h3>

This command creates mixtures of traffic between tagged end points. A traffic mix is a collection of groups of streamblocks. The traffic mix itself defines a total load that is spread across the mix (both the total load and the load units for the mix). Along with this common set of properties, the mix also has an array of components, where each component defines a group of one or more streamblocks. Each component has its own unique set of properties, including their portion of the mix's load, a set of end points, a streamblock template file, and an expansion method (e.g., route import (bgp only), route prefix distribution generation, or route specifications).<BR><BR>Streamblocks within the mix can be bound or unbound. End points for bound streamblocks are always defined by tags, and can refer to any typical streamblock end point, such as port, route or interface.<BR><BR>Streamblocks are created with a GeneratedObject relationship to their corresponding StmTemplateConfig objects, which are children of the StmTrafficMix object.

<h2>- Properties</h2>

<h3>MixInfo (input:string)<br><font size=2>"Mix Info"</font></h3>

Information that describes an entire mix of traffic in JSON string form, conforming to the MixInfoJsonSchema.

* default: <font color=#cc8888>(empty string)</font>

<h3>MixTagName (input:string)<br><font size=2>"Mix Container Tag Name"</font></h3>

The name of the mix's tag- that is, the name of the tag used in tagging the StmTrafficMix object created by this command.  If empty, the mix's StmTemplateMix object will not be tagged. This tag name is useful for both directly referencing the mix and indirectly referencing streamblocks that are generated from this mix (see AllocateTrafficMixCommand).

* default: <font color=#cc8888>(empty string)</font>

<h3>AutoExpandTemplateMix (input:bool)<br><font size=2>"Automatically expand templates in the mix"</font></h3>

If set to true, the entire mix will be expanded before this command completes. If set to false, the mix information will be loaded into an StmTrafficMix object, but streamblocks will not yet be created. Setting this to false is useful when the creation of streamblocks (that is, expanding the mix) must be done within an iterative loop at some point later in the command sequencer.

* default: true

<h3>GroupCommandTagInfo (state:string)<br><font size=2>"Group Command Tag Info"</font></h3>

A JSON formatted structure that contains the names of the tags used to refer to commands in this group. This intra-group information provides one child command with a means to reference another child command within the same group.

* default: <font color=#cc8888>(empty string)</font>

<h3>MixInfoJsonSchema (state:string)<br><font size=2>"Table Data JSON Schema"</font></h3>

JSON schema that will be used to validate the MixInfo property's value.



<h3><a id="schema.for.CreateTrafficMixCommand.MixInfoJsonSchema.h3link" href="JavaScript:;" onclick="toggle_visibility('schema.for.CreateTrafficMixCommand.MixInfoJsonSchema');">JSON Schema [+]</a></h3>

<div class="section" style="display:none;" id="schema.for.CreateTrafficMixCommand.MixInfoJsonSchema"><pre><code class="hljs json">		{
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
		          "baseTemplateFile"
		        ], 
		        "type": "object", 
		        "properties": {
		          "weight": {
		            "type": "string", 
		            "description": "Percent weight of the total load to assign to this component."
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
		                    "endpointMapping"
		                  ], 
		                  "type": "object", 
		                  "description": "Process project-level streamblocks and expand onto ports.", 
		                  "properties": {
		                    "endpointMapping": {
		                      "additionalProperties": false, 
		                      "required": [
		                        "srcBindingTagList"
		                      ], 
		                      "type": "object", 
		                      "description": "Description of end points that will be mapped on the port-level streamblocks.", 
		                      "properties": {
		                        "bidirectional": {
		                          "type": "boolean", 
		                          "description": "True if a streamblock is to be created for both directions (flipping the src and dst for the second streamblock), false if only one direction, must be false for MESH configuration."
		                        }, 
		                        "srcBindingClassList": {
		                          "items": {
		                            "type": "string", 
		                            "description": "The classname that we will search the srcBindingTagList objects for."
		                          }, 
		                          "type": "array"
		                        }, 
		                        "dstBindingTagList": {
		                          "items": {
		                            "type": "string", 
		                            "description": "List of tag names for streamblock destination binding endpoints, not used in MESH configuration."
		                          }, 
		                          "type": "array"
		                        }, 
		                        "srcBindingTagList": {
		                          "items": {
		                            "type": "string", 
		                            "description": "List of tag names for streamblock source binding endpoints."
		                          }, 
		                          "type": "array"
		                        }, 
		                        "dstBindingClassList": {
		                          "items": {
		                            "type": "string", 
		                            "description": "The classname that we will search the dstBindingTagList objects for."
		                          }, 
		                          "type": "array"
		                        }
		                      }
		                    }
		                  }
		                }
		              }
		            }, 
		            "type": "array", 
		            "description": "A list of operations that will be carried out on datamodel objects after the template is expanded."
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
		  "title": "Schema for the MixInfo of the spirent.methodology.traffic.CreateTrafficMixCommand."
		}


</code></pre></div><h3>StmTemplateMix (output:handle)<br><font size=2>"XML Container Aggregator object (StmTemplateMix)"</font></h3>

StmTemplate Mix container aggregator object

* default: <font color=#cc8888>(empty)</font>

<h3><a id="sample.for.CreateTrafficMixCommand.StmTemplateMix.h3link" href="JavaScript:;" onclick="toggle_visibility('sample.for.CreateTrafficMixCommand.StmTemplateMix');">JSON Sample [+]</a></h3>

<div class="section" style="display:none;" id="sample.for.CreateTrafficMixCommand.StmTemplateMix"><pre><code class="hljs json">

In the sample below, the mix has a total load of 2% of the line rate,
and two components, each taking half of the total mix load (each with
1% of the line rate).

The first component defines a streamblock from east to west using the
Ipv4If as its end points, where as the second component defines a
streamblock from east to west using emulated devices as its end points.

{
    "load" : 2,
    "loadUnits" : "PERCENT_LINE_RATE",
    "components" : [
        {
            "weight" : "50%",
            "baseTemplateFile" : "IPv4_Stream.xml",
            "postExpandModify" : [
                {
                    "streamBlockExpand" :
                    {
                        "endpointMapping" :
                        {
                            "bidirectional" : false,
                            "srcBindingClassList" : ["Ipv4If"],
                            "srcBindingTagList" : ["East1_ttIpv4If"],
                            "dstBindingClassList" : ["Ipv4If"],
                            "dstBindingTagList" : ["West1_ttIpv4If"]
                        }
                    }
                }
            ]
        },
        {
            "weight" : "50%",
            "baseTemplateFile" : "IPv4_Stream.xml",
            "postExpandModify" : [
                {
                    "streamBlockExpand" :
                    {
                        "endpointMapping" :
                        {
                            "bidirectional" : false,
                            "srcBindingClassList" : ["Ipv4If"],
                            "srcBindingTagList" : ["East2_ttEmulatedDevice"],
                            "dstBindingClassList" : ["Ipv4If"],
                            "dstBindingTagList" : ["West2_ttEmulatedDevice"]
                        }
                    }
                }
            ]
        }
    ]
}
<BR><BR>




In the next sample, consider how the mix's load is distributed to each component.

The second component will take 100 frames per second from the total mix load
of 200 frames per second. This is called a static value, because it isn't based
upon the total mix load. However, the combination of static values from all
components within a mix must not exceed the mix's total load value.

That leaves just 100 frames per second to divide between the first and third
components. Both of those components take only 25% of the 100 frames per second
that they are sharing, which means they each have an individual load of 25
frames per second. The combined percentage load from the components cannot exceed
100%.

{
    "load": 200,
    "loadUnits": "FRAMES_PER_SECOND",
    "components": [
        {
            "baseTemplateFile": "Ipv4_Stream.xml",
            "weight": "25 %",
            "postExpandModify": [
                {
                    "streamBlockExpand": {
                        "endpointMapping": {
                            "srcBindingTagList": ["East_Ipv4If"],
                            "dstBindingTagList": ["West_Ipv4If"]
                        }
                    }
                }
            ]
        },
        {
            "baseTemplateFile": "Ipv4_Stream.xml",
            "weight": "100",
            "postExpandModify": [
                {
                    "streamBlockExpand": {
                        "endpointMapping": {
                            "srcBindingTagList": ["East_Ipv4If"],
                            "dstBindingTagList": ["West_Ipv4If"],
                            "bidirectional": true
                        }
                    }
                }
            ]
        },
        {
            "baseTemplateFile": "MeshTemplate.xml",
            "weight": "25 %",
            "postExpandModify": [
                {
                    "streamBlockExpand": {
                        "endpointMapping": {
                            "srcBindingTagList": ["East Ipv4If"],
                            "dstBindingTagList": ["East Ipv4If"]
                        }
                    }
                }
            ]
        }
    ]
}

Note also that the first component is from east to west, the second is
bidirectional, and the third is based upon a full mesh template.
<BR><BR>


</code></pre></div><h2>- UsedIn</h2>
* RFC 2544 Throughput Test

* Routing Multi-Protocol


<script type="text/javascript">
<!--
    function toggle_visibility(id) {
       var e = document.getElementById(id);
       var caption = document.getElementById(id + '.h3link');
       var text = caption.innerHTML
       if(e.style.display == 'block')
       {
          e.style.display = 'none';
          caption.innerHTML = text.replace('[-]', '[+]');
       }
       else
       {
          e.style.display = 'block';
          caption.innerHTML = text.replace('[+]', '[-]');
       }
    }
//!-->
</script># ExpandTrafficMixCommand

Expands the traffic mix template(s) into streamblocks and attaches the streamblocks to end points designated in the traffic mix configuration. The traffic mix is defined from an StmTemplateMix object, populated with the mix information from the CreateTrafficMixCommand.

<h2>- Properties</h2>

<h3>StmTemplateMix (input:handle)<br><font size=2>"XML Container object (StmTemplateMix)"</font></h3>

Handle to an StmTemplate Mix container object that contains the traffic mix information. This value can be empty, in which case a tag name must be supplied to the TrafficMixTagName property.

* default: <font color=#cc8888>(empty)</font>

<h3>TrafficMixTagName (input:string)<br><font size=2>"Tag name for Traffic Mix"</font></h3>

Name of the tag that is attached to one or more StmTemplateMix's. Every StmTemplateMix object associated with the tag is expanded. This property can be empty, in which case a handle to an StmTemplateMix object must be provided in the StmTemplateMix property.

* default: <font color=#cc8888>(empty string)</font>

<h3>Load (input:double)<br><font size=2>"Load"</font></h3>

The total traffic load distributed across each expanded traffic mix. The value of this property is strictly a numerical value. The units that this value is to be interpreted with is found in the LoadUnit property.

* default: 10.0

<h3>LoadUnit (input:u8)<br><font size=2>"Load Unit"</font></h3>

The units to be applied to the Load property.

* default: PERCENT_LINE_RATE

		StreamBlock.EnumLoadUnit


<h3>MixInfoJsonSchema (state:string)<br><font size=2>"Table Data JSON Schema"</font></h3>

JSON schema that will be used to validate the mix information in JSON form found in the StmTemplateMix object.



<h3><a id="schema.for.ExpandTrafficMixCommand.MixInfoJsonSchema.h3link" href="JavaScript:;" onclick="toggle_visibility('schema.for.ExpandTrafficMixCommand.MixInfoJsonSchema');">JSON Schema [+]</a></h3>

<div class="section" style="display:none;" id="schema.for.ExpandTrafficMixCommand.MixInfoJsonSchema"><pre><code class="hljs json">		{
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
		          "baseTemplateFile"
		        ], 
		        "type": "object", 
		        "properties": {
		          "weight": {
		            "type": "string", 
		            "description": "Percent weight of the total load to assign to this component."
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
		                    "endpointMapping"
		                  ], 
		                  "type": "object", 
		                  "description": "Process project-level streamblocks and expand onto ports.", 
		                  "properties": {
		                    "endpointMapping": {
		                      "additionalProperties": false, 
		                      "required": [
		                        "srcBindingTagList"
		                      ], 
		                      "type": "object", 
		                      "description": "Description of end points that will be mapped on the port-level streamblocks.", 
		                      "properties": {
		                        "bidirectional": {
		                          "type": "boolean", 
		                          "description": "True if a streamblock is to be created for both directions (flipping the src and dst for the second streamblock), false if only one direction, must be false for MESH configuration."
		                        }, 
		                        "srcBindingClassList": {
		                          "items": {
		                            "type": "string", 
		                            "description": "The classname that we will search the srcBindingTagList objects for."
		                          }, 
		                          "type": "array"
		                        }, 
		                        "dstBindingTagList": {
		                          "items": {
		                            "type": "string", 
		                            "description": "List of tag names for streamblock destination binding endpoints, not used in MESH configuration."
		                          }, 
		                          "type": "array"
		                        }, 
		                        "srcBindingTagList": {
		                          "items": {
		                            "type": "string", 
		                            "description": "List of tag names for streamblock source binding endpoints."
		                          }, 
		                          "type": "array"
		                        }, 
		                        "dstBindingClassList": {
		                          "items": {
		                            "type": "string", 
		                            "description": "The classname that we will search the dstBindingTagList objects for."
		                          }, 
		                          "type": "array"
		                        }
		                      }
		                    }
		                  }
		                }
		              }
		            }, 
		            "type": "array", 
		            "description": "A list of operations that will be carried out on datamodel objects after the template is expanded."
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
		  "title": "Schema for the MixInfo of the spirent.methodology.traffic.ExpandTrafficMixCommand."
		}


</code></pre></div><font color="red">MISSING JSON SAMPLE</font>

<h2>- UsedIn</h2>
* Routing Multi-Protocol


<script type="text/javascript">
<!--
    function toggle_visibility(id) {
       var e = document.getElementById(id);
       var caption = document.getElementById(id + '.h3link');
       var text = caption.innerHTML
       if(e.style.display == 'block')
       {
          e.style.display = 'none';
          caption.innerHTML = text.replace('[-]', '[+]');
       }
       else
       {
          e.style.display = 'block';
          caption.innerHTML = text.replace('[+]', '[-]');
       }
    }
//!-->
</script>