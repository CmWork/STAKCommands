# AllocateRouteMixCountCommand

Allocate total route count to components in the route mix

<h2>- Properties</h2>

<h3>RouteMixList (input:handle)<br><font size=2>"Route Mix"</font></h3>

Route Mix Object Handles

* default: <font color=#cc8888>(empty)</font>

<h3>RouteMixTagList (input:string)<br><font size=2>"Tag name for Route Mix"</font></h3>

Tag names associated with the Route Mix objects

* default: <font color=#cc8888>(empty string)</font>

<h3>RouteCount (input:u64)<br><font size=2>"Route Count"</font></h3>

Total number of routes

* default: 10

<h3>MixInfoJsonSchema (state:string)<br><font size=2>"Route Mix Info JSON Schema"</font></h3>

JSON schema that will be used to validate the MixInfo property's value.

* default: <font color=#cc8888>(empty string)</font>


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
</script># BgpImportRoutesCommand

Expand Import Route Command

<h2>- Properties</h2>

<h3>RouterTagList (input:string)<br><font size=2>"Router Tag List"</font></h3>

List of tag names, which tag BgpRouterConfig objects, that we will import BgpRouteConfig objects under.

* default: <font color=#cc8888>(empty string)</font>

<h3>BgpImportParamsTagName (input:string)<br><font size=2>"BgpImportRouteTableParams tag name"</font></h3>

The tag name that identifies the BgpImportRouteTableParams object that the BgpImportRouteTableCommand will use to generate routes

* default: ttImportRouteParams

<h3>CreatedRoutesTagName (input:string)<br><font size=2>"New routes will be tagged with this"</font></h3>

The tag name that new routes made by the BgpImportRouteTableCommand will be subsequently tagged with

* default: ttImportRouteParams

<h2>- UsedIn</h2>
* BGP Route Reflector Test


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
</script># CreateRouteMixCommand

<h3>Extends spirent.methodology.CreateTemplateMixCommand.</h3>

Command for creating mixtures of route counts among route objects on tagged router config objects.

<h2>- Properties</h2>

<h3>MixInfo (input:string)<br><font size=2>"Mix Info"</font></h3>

JSON string representation of the mix (including table data)

* default: <font color=#cc8888>(empty string)</font>

<h3>MixTagName (input:string)<br><font size=2>"Mix Container Tag Name"</font></h3>

Name to use when tagging the output StmTemplateMix.  If left blank, StmTemplateMix will not be tagged.

* default: <font color=#cc8888>(empty string)</font>

<h3>AutoExpandTemplateMix (input:bool)<br><font size=2>"Automatically expand templates in the mix"</font></h3>

Automatically expand templates.

* default: true

<h3>GroupCommandTagInfo (state:string)<br><font size=2>"Group Command Tag Info"</font></h3>

JSON structure containing the names of the tags used to refer to commands in this group.

* default: <font color=#cc8888>(empty string)</font>

<h3>MixInfoJsonSchema (state:string)<br><font size=2>"Table Data JSON Schema"</font></h3>

JSON schema that will be used to validate the MixInfo property's value.



<h3><a id="schema.for.CreateRouteMixCommand.MixInfoJsonSchema.h3link" href="JavaScript:;" onclick="toggle_visibility('schema.for.CreateRouteMixCommand.MixInfoJsonSchema');">JSON Schema [+]</a></h3>

<div class="section" style="display:none;" id="schema.for.CreateRouteMixCommand.MixInfoJsonSchema"><pre><code class="hljs json">		{
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


</code></pre></div><h3>TargetObjectList (input:handle)<br><font size=2>"Target Object List"</font></h3>

List of StmProtocolMix, StmTemplateConfig, EmulatedDevice, or RouterConfig objects, that we will expand RouteConfig objects under

* default: <font color=#cc8888>(empty)</font>

<h3>TargetObjectTagList (input:string)<br><font size=2>"Target Object Tag List"</font></h3>

List of tag names, which tag StmProtocolMix, StmTemplateConfig, EmulatedDevice, or RouterConfig objects, that we will expand RouteConfig objects under.

* default: <font color=#cc8888>(empty string)</font>

<h3>StmTemplateMix (output:handle)<br><font size=2>"XML Container Aggregator object (StmTemplateMix)"</font></h3>

StmTemplate Mix container aggregator object

* default: <font color=#cc8888>(empty)</font>

<font color="red">MISSING JSON SAMPLE</font>

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
</script># ExpandRouteMixCommand

Expand Route Mix Command

<h2>- Properties</h2>

<h3>TargetObjectList (input:handle)<br><font size=2>"Target Object List"</font></h3>

List of StmProtocolMix, StmTemplateConfig, EmulatedDevice, or RouterConfig objects, that we will expand RouteConfig objects under

* default: <font color=#cc8888>(empty)</font>

<h3>TargetObjectTagList (input:string)<br><font size=2>"Target Object Tag List"</font></h3>

List of tag names, which tag StmProtocolMix, StmTemplateConfig, EmulatedDevice, or RouterConfig objects, that we will expand RouteConfig objects under.

* default: <font color=#cc8888>(empty string)</font>

<h3>SrcObjectList (input:handle)<br><font size=2>"Source Object List"</font></h3>

List of handles to StmTemplateMix objects, created by CreateRouteMixCommand, that contain the XML for RouteConfig objects to expand.

* default: <font color=#cc8888>(empty)</font>

<h3>SrcObjectTagList (input:string)<br><font size=2>"Source Object Tag List"</font></h3>

List of tag names to StmTemplateMix objects, created by CreateRouteMixCommand, that contain the XML for RouteConfig objects to expand.

* default: <font color=#cc8888>(empty string)</font>

<h3>RouteCount (input:u32)<br><font size=2>"Route Count"</font></h3>

Route Count

* default: 1000

<h3>MixInfoJsonSchema (state:string)<br><font size=2>"Table Data JSON Schema"</font></h3>

JSON schema that will be used to validate the MixInfo property's value.



<h3><a id="schema.for.ExpandRouteMixCommand.MixInfoJsonSchema.h3link" href="JavaScript:;" onclick="toggle_visibility('schema.for.ExpandRouteMixCommand.MixInfoJsonSchema');">JSON Schema [+]</a></h3>

<div class="section" style="display:none;" id="schema.for.ExpandRouteMixCommand.MixInfoJsonSchema"><pre><code class="hljs json">		{
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
</script># RoutePrefixDistributionCommand

Route Prefix Distribution Command

<h2>- Properties</h2>

<h3>RouterTagList (input:string)<br><font size=2>"Router Tag List"</font></h3>

List of tag names, which tag BgpRouterConfig objects, that we will import RouteConfig objects under.

* default: <font color=#cc8888>(empty string)</font>

<h3>SrcObjectTagName (input:string)<br><font size=2>"Source Object Tag Name tag name"</font></h3>

The tag name that identifies the ProtocolRouteGenParams object that the RouteGenApplyCommand will use to generate routes

* default: ttProtocolRouteGenParams

<h3>CreatedRoutesTagName (input:string)<br><font size=2>"Created Routes Tag Name"</font></h3>

The tag name that new routes made by the RouteGenApplyCommand will be subsequently tagged with

* default: ttRoutePrefixParams


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