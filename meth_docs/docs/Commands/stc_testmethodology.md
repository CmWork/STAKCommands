# AddRowToDbTableCommand

Add queried results to a new or existing table.

<h2>- Properties</h2>

<h3>SrcDatabase (input:u8)<br><font size=2>"Source Database"</font></h3>

Select source database(s) to execute Sql query.

* default: ALL_ITERATION

		EnumSourceDatabase
		    LAST_ITERATION = 0
		    SUMMARY = 1
		    ALL_ITERATION = 2


<h3>DstDatabase (input:u8)<br><font size=2>"Destination Database"</font></h3>

Select destination database to create new table.

* default: SUMMARY

		EnumDestinationDatabase
		    LAST_ITERATION = 0
		    SUMMARY = 1


<h3>SqlCreateTable (input:string)<br><font size=2>"Create Table Sql Statement"</font></h3>

Specify a table name for an existing destination table or a Create Table Sql statement for a new destination table. If the table exists, a new one shall not be created.

* default: CREATE TABLE NewTableName ('Column1' INTEGER, 'Column2' TIMESTAMP)

<h3>SqlQuery (input:string)<br><font size=2>"Source Data Sql Query"</font></h3>

Sql query for source data. Queried results shall be populated in new or existing table specified in Create Table Sql Statement field. The number of columns in the query must match the number of columns in the table.

* default: SELECT Id, CreatedTime From DataSet

<h2>- UsedIn</h2>
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
</script># AddTemplateObjectCommand

Add a new STC object to the template

<h2>- Properties</h2>

<h3>StmTemplateConfig (input:handle)<br><font size=2>"StmTemplateConfig"</font></h3>

StmTemplateConfig

* default: <font color=#cc8888>(empty)</font>

<h3>ParentTagName (input:string)<br><font size=2>"Parent Tag Name"</font></h3>

Name of the tag from which parent objects will be found to add new objects to under

* default: <font color=#cc8888>(empty string)</font>

<h3>TagName (input:string)<br><font size=2>"Tag Name"</font></h3>

Name of a new tag to create and attach to the added objects

* default: <font color=#cc8888>(empty string)</font>

<h3>ClassName (input:string)<br><font size=2>"Class Name"</font></h3>

Class name of the object

* default: <font color=#cc8888>(empty string)</font>

<h3>PropertyList (input:string)<br><font size=2>"Property List"</font></h3>

List of property IDs on the newly created object to configure new values for.  Position in this list MUST map to position in the ValueList.

* default: <font color=#cc8888>(empty string)</font>

<h3>ValueList (input:string)<br><font size=2>"Value List"</font></h3>

List of values to configure on the newly created object.  Position in this list MUST map to position in the PropertyList.

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
</script># BenchmarkStabilityIteratorCommand

<h3>Extends spirent.methodology.IteratorCommand.</h3>

Discrete step size binary or step search followed by stability test with backoff

<h2>- Properties</h2>

<h3>EnableStabilityBackoff (input:bool)<br><font size=2>"Enable Stability Backoff"</font></h3>

Enable stability backoff iteration once a converged value is found.  If false, iteration will end once a converged value is found.

* default: true

<h3>IterMode (input:u8)<br><font size=2>"Iteration Mode"</font></h3>

Iteration mode

* default: STEP

		EnumIterMode
		    STEP = 1
		    BINARY = 2


<h3>StepVal (input:double)<br><font size=2>"Step value"</font></h3>

Step value

* default: 10

<h3>ValueType (input:u8)<br><font size=2>"Value type"</font></h3>

Value type (list or range)

* default: RANGE

		EnumValueType
		    RANGE = 1
		    LIST = 2


<h3>ValueList (input:string)<br><font size=2>"List of values"</font></h3>

List of values to test

* default: <font color=#cc8888>(empty string)</font>

<h3>RepeatCount (input:u32)<br><font size=2>"Repeat Count"</font></h3>

Number of times to repeat an iteration

* default: 5

<h3>SuccessPercent (input:double)<br><font size=2>"Success Percent"</font></h3>

Number of times a repeated value has to pass to be considered stable

* default: 100

<h3>CurrIndex (state:u32)<br><font size=2>"Current Index"</font></h3>

Current list value's index

* default: 0

<h3>IterState (state:u8)<br><font size=2>"Iterator state"</font></h3>

Specifies what part of the search the iterator is in (goal-seeking or stability backoff)

* default: SEARCH

		EnumIterState
		    SEARCH = 1
		    STABILITY = 2


<h3>SearchIteration (state:u32)<br><font size=2>"Goal-seeking Test Iteration Number"</font></h3>

Iteration number used during goal-seek testing

* default: 0

<h3>SearchMinFail (state:double)<br><font size=2>"Minimum fail value"</font></h3>

Minimum failing value encountered during search

* default: <font color=#cc8888>(empty)</font>

<h3>SearchMaxPass (state:double)<br><font size=2>"Maximum pass value"</font></h3>

Maximum passing value encountered during search

* default: <font color=#cc8888>(empty)</font>

<h3>StabilityIteration (state:u32)<br><font size=2>"Stability Test Iteration Number"</font></h3>

Iteration number used during stability testing

* default: 0

<h3>StabilityTrialNum (state:u32)<br><font size=2>"Stability Test Trial Number"</font></h3>

Trial number for a particular test value during stability testing

* default: 0

<h3>StabilitySuccessCount (state:u32)<br><font size=2>"Stability Success Count"</font></h3>

Number of successful trials in a iteration during stability testing

* default: 0

<h3>IsConverged (output:bool)<br><font size=2>"Is Converged"</font></h3>

Did the iterator converge?

* default: false

<h3>ConvergedVal (output:string)<br><font size=2>"Converged Value"</font></h3>

Value the iterator converged on

* default: <font color=#cc8888>(empty string)</font>

<h3>StableValue (output:string)<br><font size=2>"Stable value"</font></h3>

Stable value

* default: 0

<h3>FoundStableValue (output:bool)<br><font size=2>"Found a stable value"</font></h3>

Flag indicating a stable value was found

* default: false

<h3>BreakOnFail (input:bool)<br><font size=2>"Break on fail"</font></h3>

Break out of the test when an iteration fails

* default: false

<h3>MinVal (input:double)<br><font size=2>"Minimum value"</font></h3>

Minimum value

* default: 0

<h3>MaxVal (input:double)<br><font size=2>"Maximum value"</font></h3>

Maximum value

* default: 100

<h3>PrevIterVerdict (input:bool)<br><font size=2>"Previous iteration result"</font></h3>

Result of the previous iteration

* default: true

<h3>Iteration (state:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<h3>CurrVal (state:string)<br><font size=2>"Current value"</font></h3>

Value to use in the current iteration

* default: <font color=#cc8888>(empty string)</font>

<h3>ResetState (state:bool)<br><font size=2>"Reset State"</font></h3>

Reset state properties

* default: false

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
</script># CompleteIterationCommand

Collect and summarize results for current iteration

<h2>- Properties</h2>

<h2>- UsedIn</h2>
* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

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
</script># ConfigRelationCommand

Add or remove a relation between tagged BLL objects

<h2>- Properties</h2>

<h3>SrcTagName (input:string)<br><font size=2>"Source Tag Name"</font></h3>

Name of the tag from which the source object(s) will be found

* default: <font color=#cc8888>(empty string)</font>

<h3>TargetTagName (input:string)<br><font size=2>"Target Tag Name"</font></h3>

Name of the tag from which the target object(s) will be found

* default: <font color=#cc8888>(empty string)</font>

<h3>RelationName (input:string)<br><font size=2>"Relation Name"</font></h3>

Name of the relation to add or remove

* default: <font color=#cc8888>(empty string)</font>

<h3>RemoveRelation (input:bool)<br><font size=2>"Remove Relation"</font></h3>

Remove the relation of the given type

* default: false


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
</script># ConfigTemplatePdusCommand

This command will configure PDUs in the Streamblock template's FrameConfig that itself is found in the StmTemplateConfig, using the information from PduInfo property.

<h2>- Properties</h2>

<h3>StmTemplateConfig (input:handle)<br><font size=2>"StmTemplateConfig"</font></h3>

StmTemplateConfig handle

* default: <font color=#cc8888>(empty)</font>

<h3>TemplateElementTagNameList (input:string)<br><font size=2>"Template Element Tag Name List"</font></h3>

List of tag names that refer to the targeted stream block (XML elements) in the template.

* default: <font color=#cc8888>(empty string)</font>

<h3>PduPropertyList (input:string)<br><font size=2>"PDU Information Property List"</font></h3>

List of properties to modify PDU information within streamblocks' FrameConfig properties.

* default: <font color=#cc8888>(empty string)</font>

<h3>PduValueList (input:string)<br><font size=2>"PDU Information Value List"</font></h3>

List of values to modify PDU information within streamblocks' FrameConfig properties.

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
</script># ConfigTemplateRelationCommand

Add or remove a relation in the template

<h2>- Properties</h2>

<h3>StmTemplateConfig (input:handle)<br><font size=2>"StmTemplateConfig"</font></h3>

StmTemplateConfig

* default: <font color=#cc8888>(empty)</font>

<h3>SrcTagName (input:string)<br><font size=2>"Source Tag Name"</font></h3>

Name of the tag from which the source object will be found

* default: <font color=#cc8888>(empty string)</font>

<h3>TargetTagName (input:string)<br><font size=2>"Target Tag Name"</font></h3>

Name of the tag from which the target object will be found

* default: <font color=#cc8888>(empty string)</font>

<h3>RelationName (input:string)<br><font size=2>"Relation Name"</font></h3>

Name of the relation to add or remove

* default: <font color=#cc8888>(empty string)</font>

<h3>RemoveRelation (input:bool)<br><font size=2>"Remove Relation"</font></h3>

Remove the relation of the given type

* default: false


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
</script># ConfigTemplateStmPropertyModifierCommand

Add or configure an StmPropertyModifier in the template

<h2>- Properties</h2>

<h3>StmTemplateConfig (input:handle)<br><font size=2>"StmTemplateConfig"</font></h3>

StmTemplateConfig

* default: <font color=#cc8888>(empty)</font>

<h3>TagName (input:string)<br><font size=2>"Tag Name"</font></h3>

Name of the Tag referencing an StmPropertyModifier object to modify in the template.  If an StmPropertyModifier is being created, this is the name that will be used for a tag that references the StmPropertyModifier.

* default: <font color=#cc8888>(empty string)</font>

<h3>TargetObjectTagName (input:string)<br><font size=2>"Target Object's Tag Name"</font></h3>

Name of the Tag referencing the target object this modifier is being applied to.  If configuring an existing modifier, this can be left empty.

* default: <font color=#cc8888>(empty string)</font>

<h3>ObjectName (input:string)<br><font size=2>"Object Name"</font></h3>

Class name of the object being modified.  If configuring an existing modifier, this can be left empty. 

* default: <font color=#cc8888>(empty string)</font>

<h3>PropertyName (input:string)<br><font size=2>"Property Name"</font></h3>

Name of the property being modified.  If configuring an existing modifier, this can be left empty. 

* default: <font color=#cc8888>(empty string)</font>

<h3>StartList (input:string)<br><font size=2>"Start Value List"</font></h3>

List of modifier start values

* default: <font color=#cc8888>(empty string)</font>

<h3>StepList (input:string)<br><font size=2>"Step Value List"</font></h3>

List of modifier step values

* default: <font color=#cc8888>(empty string)</font>

<h3>RepeatList (input:u32)<br><font size=2>"Repeat Value List"</font></h3>

List of modifier repeat values

* default: 0

<h3>RecycleList (input:u32)<br><font size=2>"Recycle Value List"</font></h3>

List of modifier recycle values

* default: 0

<h3>ModifierType (input:u8)<br><font size=2>"Modifier Type"</font></h3>

The type of modifier to add or configure.  If a modifier already exists with the given tag but is of different type, it will be changed to use the new type.

* default: RANGE

		EnumModifierType
		    RANGE = 0


<h3>TargetObjectStepList (input:string)<br><font size=2>"Target Object Step List"</font></h3>

List of step value to apply to start value(s) when a new target object is encountered.

* default: <font color=#cc8888>(empty string)</font>

<h3>ResetOnNewTargetObject (input:bool)<br><font size=2>"Reset Start Value On New Target Object"</font></h3>

Reset the start value each time a new target (usually parent) object of the objects being modified is encountered.

* default: true

<h2>- UsedIn</h2>
* L3 QoS DiffServ

* BGP Route Reflector Test

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* ACL Basic Test


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
</script># CreateMethodologyChartCommand

<h3>Extends spirent.methodology.ResultBaseCommand.</h3>

Export Chart

<h2>- Properties</h2>

<h3>ChartTemplateJsonFileName (input:inputFilePath)<br><font size=2>"Chart Template File"</font></h3>

Chart template file in JSON format. May use one of the provided basic templates: Line_Template.json and Column_Template.json.

* default: Line_Template.json

<h3>Title (input:string)<br><font size=2>"Chart Title"</font></h3>

Title displayed at the top of the chart.

* default: Result Node Param Handles

<h3>XAxisTitle (input:string)<br><font size=2>"X Axis Title"</font></h3>

Title displayed along the X axis.

* default: Id

<h3>XAxisCategories (input:string)<br><font size=2>"X Axis Categories"</font></h3>

X axis categories specified as a list of strings or SQL queries. Used to label the tick marks along the X axis.

* default: <font color=#cc8888>(empty string)</font>

<h3>YAxisTitle (input:string)<br><font size=2>"Y Axis Title"</font></h3>

Title displayed along the Y axis.

* default: Handle

<h3>YAxisCategories (input:string)<br><font size=2>"Y Axis Categories"</font></h3>

Y axis categories specified as a list of strings or SQL queries. Used to label the tick marks along the Y axis.

* default: <font color=#cc8888>(empty string)</font>

<h3>Series (input:string)<br><font size=2>"Series' Data"</font></h3>

Set of data to be plotted on the chart specified as a list of strings or SQL queries. Each list element is a series. The string format to plot a single data type is: 1, 2, 3, 4. Plotting two data types is: [1, 1], [2, 2].

* default: <font color=#cc8888>(empty string)</font>

<h3>TemplateModifier (input:string)<br><font size=2>"Template Modifier"</font></h3>

Modify chart properties by specifying a string in JSON format that will be appended to the result file. Specified properties will be merged with and overwrite any existing properies in the chart template file. Follows the HighCharts API. Ex. {"yAxis": {"title": {"text": "Modified Label"}}} SQL Queries can be inserted to the JSON string by delimiting the queries with {{ and }}.

* default: {"series":[{"name": "Handles"}]}

<h3>SrcDatabase (input:u8)<br><font size=2>"Source Database"</font></h3>

Select source database(s) to execute the Sql queries.

* default: SUMMARY

		EnumSourceDatabase
		    LAST_ITERATION = 0
		    SUMMARY = 1
		    ALL_ITERATION = 2


<h3>ReportGroup (input:u8)<br><font size=2>"Report Group"</font></h3>

Determines where the results will be displayed on the results page. Group 0 is the highest priority and will be displayed before Group 3, Group 2, etc. SUMMARY will be displayed at the very top in the summary section.

* default: GROUP_2

		spirent.methodology.ResultBaseCommand.EnumReportGroup


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
</script># CreateProtocolMixCommand

<h3>Extends spirent.methodology.CreateTemplateMixCommand.</h3>

Command for creating mixtures of protocols on an Emulated Device block.

<h2>- Properties</h2>

<h3>MixInfo (input:string)<br><font size=2>"Mix Info"</font></h3>

JSON string representation of the mix (including table data)

* default: <font color=#cc8888>(empty string)</font>

<h3>MixTagName (input:string)<br><font size=2>"Mix Container Tag Name"</font></h3>

Name to use when tagging the output StmProtocolMix.  If left blank, StmProtocolMix will not be tagged.

* default: <font color=#cc8888>(empty string)</font>

<h3>PortGroupTagList (input:string)<br><font size=2>"Port Group Tag"</font></h3>

Tag name representing the port group on which devices and protocols should be expanded on.

* default: <font color=#cc8888>(empty string)</font>

<h3>GroupCommandTagInfo (state:string)<br><font size=2>"Group Command Tag Info"</font></h3>

JSON structure containing the names of the tags used to refer to commands in this group.

* default: <font color=#cc8888>(empty string)</font>

<h3>MixInfoJsonSchema (state:string)<br><font size=2>"Table Data JSON Schema"</font></h3>

JSON schema that will be used to validate the TableData property's value.



<h3><a id="schema.for.CreateProtocolMixCommand.MixInfoJsonSchema.h3link" href="JavaScript:;" onclick="toggle_visibility('schema.for.CreateProtocolMixCommand.MixInfoJsonSchema');">JSON Schema [+]</a></h3>

<div class="section" style="display:none;" id="schema.for.CreateProtocolMixCommand.MixInfoJsonSchema"><pre><code class="hljs json">		{
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


</code></pre></div><h3>AutoExpandTemplateMix (input:bool)<br><font size=2>"Automatically expand templates in the mix"</font></h3>

Automatically expand templates.

* default: true

<h3>StmTemplateMix (output:handle)<br><font size=2>"XML Container Aggregator object (StmTemplateMix)"</font></h3>

StmTemplate Mix container aggregator object

* default: <font color=#cc8888>(empty)</font>

<font color="red">MISSING JSON SAMPLE</font>

<h2>- UsedIn</h2>
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
</script># CreateTemplateConfigCommand

Create an StmTemplateConfig by load an XML template and modifying it.

<h2>- Properties</h2>

<h3>AutoExpandTemplate (input:bool)<br><font size=2>"Automatically Expand Template"</font></h3>

Expand template into EmulatedDevices, Streamblocks, etc.

* default: true

<h3>StmTemplateMix (input:handle)<br><font size=2>"Parent StmTemplateMix object"</font></h3>

Handle of an StmTemplateMix object to use for the parent of the created StmTemplateConfig.

* default: <font color=#cc8888>(empty)</font>

<h3>InputJson (input:string)<br><font size=2>"JSON Input"</font></h3>

JSON string representation of parameters to load and modify template(s) into the StmTemplateConfig.

* default: {"baseTemplateFile": "IPv4_NoVlan.xml"}

<h3>CopiesPerParent (input:u32)<br><font size=2>"Number of copies to make per Target Tag object"</font></h3>

Number of copies of the template to make per Target Tag object

* default: 1

<h3>SrcTagList (input:string)<br><font size=2>"Source Tag List"</font></h3>

List of tags that indicate where in the XML template the config will be expanded from

* default: <font color=#cc8888>(empty string)</font>

<h3>TargetTagList (input:string)<br><font size=2>"Target Tag List"</font></h3>

List of tags that indicate where in the STC configuration the template will be copied to.  If TargetTagList is empty, the target will be assumed to be Project.

* default: <font color=#cc8888>(empty string)</font>

<h3>InputJsonSchema (state:string)<br><font size=2>"Input JSON Schema"</font></h3>

JSON schema that will be used to validate the InputJson property's value.



<h3><a id="schema.for.CreateTemplateConfigCommand.InputJsonSchema.h3link" href="JavaScript:;" onclick="toggle_visibility('schema.for.CreateTemplateConfigCommand.InputJsonSchema');">JSON Schema [+]</a></h3>

<div class="section" style="display:none;" id="schema.for.CreateTemplateConfigCommand.InputJsonSchema"><pre><code class="hljs json">		{
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


</code></pre></div><h3>StmTemplateConfig (output:handle)<br><font size=2>"XML container object (StmTemplateConfig)"</font></h3>

StmTemplateConfig container object

* default: <font color=#cc8888>(empty)</font>

<font color="red">MISSING JSON SAMPLE</font>

<h2>- UsedIn</h2>
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
</script># DeleteTemplateObjectCommand

Delete an object and all of its children from the template

<h2>- Properties</h2>

<h3>StmTemplateConfig (input:handle)<br><font size=2>"StmTemplateConfig"</font></h3>

StmTemplateConfig

* default: <font color=#cc8888>(empty)</font>

<h3>TagName (input:string)<br><font size=2>"Tag Name"</font></h3>

Name of the tag referring to the object to delete

* default: <font color=#cc8888>(empty string)</font>

<h3>ClassName (input:string)<br><font size=2>"Class Name"</font></h3>

Class name of the object

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
</script># DeleteTemplatesAndGeneratedObjectsCommand

Deletes StmTemplateConfigs and objects generated from expansion of the templates

<h2>- Properties</h2>

<h3>DeleteStmTemplateConfigs (input:bool)<br><font size=2>"Delete StmTemplateConfig objects"</font></h3>

Deletes StmTemplateConfig objects when True, skip them when False

* default: true

<h2>- UsedIn</h2>
* L3 QoS DiffServ

* BGP Route Reflector Test

* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* Widgets Test

* Basic Traffic Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* ACL Basic Test

* ITU-T Y.1564 Microburst Test

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
</script># EndOfTestCommand

Aggregates and writes out test results

<h2>- Properties</h2>

<h2>- UsedIn</h2>
* L3 QoS DiffServ

* BGP Route Reflector Test

* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* Widgets Test

* Basic Traffic Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* ACL Basic Test

* ITU-T Y.1564 Microburst Test

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
</script># ExpandProtocolMixCommand

<h3>Extends spirent.methodology.ExpandTemplateMixCommand.</h3>

Expand a Protocol Mix

<h2>- Properties</h2>

<h3>TagName (input:string)<br><font size=2>"Tag name for the Template Mix"</font></h3>

Tag name referencing an existing StmProtocolMix

* default: <font color=#cc8888>(empty string)</font>

<h3>DeviceCount (input:u32)<br><font size=2>"Device Count"</font></h3>

Device Count

* default: 10

<h3>PortGroupTagList (input:string)<br><font size=2>"Port Group Tag"</font></h3>

Tag name representing the port group on which devices and protocols should be expanded on.

* default: <font color=#cc8888>(empty string)</font>

<h3>StmTemplateMix (input:handle)<br><font size=2>"XML Container object (StmTemplateMix)"</font></h3>

StmTemplate Mix container object

* default: <font color=#cc8888>(empty)</font>

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
</script># ExpandTemplateCommand

Expand an XML template across ports

<h2>- Properties</h2>

<h3>StmTemplateConfigList (input:handle)<br><font size=2>"StmTemplateConfig List"</font></h3>

List of StmTemplateConfig objects

* default: <font color=#cc8888>(empty)</font>

<h3>CopiesPerParent (input:u32)<br><font size=2>"Number of copies to make per Target Tag object"</font></h3>

Number of copies of the template to make per Target Tag object

* default: 1

<h3>SrcTagList (input:string)<br><font size=2>"Source Tag List"</font></h3>

List of tags that indicate where in the XML template the config will be copied from

* default: <font color=#cc8888>(empty string)</font>

<h3>TargetTagList (input:string)<br><font size=2>"Target Tag List"</font></h3>

List of tags that indicate where in the STC configuration the template will be copied to.  If TargetTagList is empty, the target will be assumed to be Project.

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
</script># ExportDbChartCommand

<h3>Extends spirent.methodology.ResultBaseCommand.</h3>

Export Chart

<h2>- Properties</h2>

<h3>ChartTemplateJsonFileName (input:inputFilePath)<br><font size=2>"Chart Template File"</font></h3>

Chart Template JSON File Location

* default: <font color=#cc8888>(empty)</font>

<h3>Title (input:string)<br><font size=2>"Chart Title"</font></h3>

Chart Title

* default: My Chart

<h3>XAxisTitle (input:string)<br><font size=2>"X Axis Title"</font></h3>

X Axis Title

* default: My X Axis

<h3>XAxisCategories (input:string)<br><font size=2>"X Axis Categories"</font></h3>

X Axis Categories (can be a string or SQL query). Used to label the tick marks along the X axis

* default: <font color=#cc8888>(empty string)</font>

<h3>YAxisTitle (input:string)<br><font size=2>"Y Axis Title"</font></h3>

Y Axis Title

* default: My Y Axis

<h3>YAxisCategories (input:string)<br><font size=2>"Y Axis Categories"</font></h3>

Y Axis Categories (can be a string or SQL query). Used to label the tick marks along the Y axis

* default: <font color=#cc8888>(empty string)</font>

<h3>Series (input:string)<br><font size=2>"Series' Data"</font></h3>

Set of data to be plotted on the chart (can be given as strings or SQL queries) Ex. String format for SeriesDataType(Single): 1, 2, 3, 4 SeriesDataType(Pair): [1, 1], [2, 2]

* default: <font color=#cc8888>(empty string)</font>

<h3>SeriesDataType (input:u8)<br><font size=2>"Series Data Type"</font></h3>

Series data can be given as a single or pair type. SINGLE = only Y values, X values are calculated automaticatlly. PAIR = [x,y] value pairs

* default: SINGLE

		EnumSeriesDataType
		    SINGLE = 1
		    PAIR = 2


<h3>CustomModifier (input:string)<br><font size=2>"Custom Modifier"</font></h3>

JSON string that will be appended to the JSON result file which is used to modify chart properties. Follows HighCharts API. Ex. {"yAxis": {"title": {"text": "Modified Label"}}} SQL Queries can be inserted to the JSON string by delimiting the queries with {{ and }}

* default: <font color=#cc8888>(empty string)</font>

<h3>UseMultipleResultsDatabases (input:bool)<br><font size=2>"Has Multiple Results Databases"</font></h3>

Used when there are multiple results databases (SaveResults LoopMode = Append). All active results databases will be queried. If set to True and only one results database exists (SaveResults LoopMode = Overwrite), an error will occur.

* default: false

<h3>UseSummary (input:bool)<br><font size=2>"Use the summery db only"</font></h3>

Use the summary db instead of iteration dbs. Only valid if UseMultipleResultsDatabases is False.

* default: false

<h3>ReportGroup (input:u8)<br><font size=2>"Report Group"</font></h3>

Determines where the results will be displayed on the results page. Group 0 is the highest priority and will be displayed before Group 3, Group 2, etc. SUMMARY will be displayed at the very top in the summary section.

* default: GROUP_2

		spirent.methodology.ResultBaseCommand.EnumReportGroup


<h2>- UsedIn</h2>
* ITU-T Y.1564 Microburst Test

* BGP Route Reflector Test

* Widgets Test


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
</script># ExportDynamicResultViewDataCommand

<h3>Extends spirent.methodology.VerifyBaseCommand.</h3>

Export dynamic result view data to the test report.

<h2>- Properties</h2>

<h3>DynamicResultViewNameList (input:string)<br><font size=2>"Dynamic Result View Name List"</font></h3>

Dynamic Result View Name List.

* default: <font color=#cc8888>(empty string)</font>

<h3>ExportDisabledAutoGroupData (input:bool)<br><font size=2>"Export Disabled Auto Group Data"</font></h3>

Export disabled auto group data for drilldown results.

* default: false

<h3>DisplayNameList (input:string)<br><font size=2>"Display Name List"</font></h3>

Title to display for this result section in the report file. Maps 1-1 with dynamic result view list.

* default: <font color=#cc8888>(empty string)</font>

<h3>ApplyVerdictToSummary (input:bool)<br><font size=2>"Apply Verdict To Summary"</font></h3>

Apply Verdict To Test verdict.

* default: true


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
</script># IterationGroupCommand

<h3>Extends stak.StakGroupCommand.</h3>

Iteration Group

<h2>- Properties</h2>

<h3>ObjectList (input:handle)<br><font size=2>"Object List"</font></h3>

List of objects to configure

* default: <font color=#cc8888>(empty)</font>

<h2>- UsedIn</h2>
* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

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
</script># IteratorConfigFrameSizeCommand

<h3>Extends spirent.methodology.IteratorConfigCommand.</h3>

Configure the frame size on a group of tagged streamblocks

<h2>- Properties</h2>

<h3>ObjectList (input:handle)<br><font size=2>"Object List"</font></h3>

List of objects to configure

* default: <font color=#cc8888>(empty)</font>

<h3>IgnoreEmptyTags (input:bool)<br><font size=2>"Ignore Empty Tags"</font></h3>

If set to false, tags must point to at least one object

* default: false

<h3>TagList (input:string)<br><font size=2>"Tag List"</font></h3>

List of Tags from which to get objects to be configured

* default: <font color=#cc8888>(empty string)</font>

<h3>CurrVal (input:string)<br><font size=2>"Current value"</font></h3>

Value to use in the current iteration

* default: <font color=#cc8888>(empty string)</font>

<h3>Iteration (input:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<h2>- UsedIn</h2>
* ITU-T Y.1564 CBS and EBS Burst Test

* RFC 2544 Throughput Test

* ACL Performance Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 Service Performance Test


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
</script># IteratorConfigMixParamsCommand

<h3>Extends spirent.methodology.IteratorConfigCommand.</h3>

dummy

<h2>- Properties</h2>

<h3>StmTemplateMix (input:handle)<br><font size=2>"StmTemplateMix"</font></h3>

StmTemplateMix handle

* default: <font color=#cc8888>(empty)</font>

<h3>TagData (input:string)<br><font size=2>"tag Data"</font></h3>



* default: <font color=#cc8888>(empty string)</font>

<h3>MixJsonSchema (state:string)<br><font size=2>"Mix JSON Schema"</font></h3>

JSON schema that will be used to validate the StmTemplateMix JSON contents.



<h3><a id="schema.for.IteratorConfigMixParamsCommand.MixJsonSchema.h3link" href="JavaScript:;" onclick="toggle_visibility('schema.for.IteratorConfigMixParamsCommand.MixJsonSchema');">JSON Schema [+]</a></h3>

<div class="section" style="display:none;" id="schema.for.IteratorConfigMixParamsCommand.MixJsonSchema"><pre><code class="hljs json">		{
		  "required": [
		    "components"
		  ], 
		  "type": "object", 
		  "properties": {
		    "components": {
		      "items": {
		        "required": [
		          "weight", 
		          "baseTemplateFile"
		        ], 
		        "type": "object", 
		        "properties": {
		          "appliedValue": {
		            "type": "number", 
		            "description": "Load actually assigned to this component.  Autocalculated, do not set."
		          }, 
		          "tagPrefix": {
		            "type": "string", 
		            "description": "String that will be prefixed to all tags loaded and used in this template."
		          }, 
		          "weight": {
		            "type": "string", 
		            "description": "Percent weight of the total load to assign to this component."
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


</code></pre></div><h3>ObjectList (input:handle)<br><font size=2>"Object List"</font></h3>

List of objects to configure

* default: <font color=#cc8888>(empty)</font>

<h3>IgnoreEmptyTags (input:bool)<br><font size=2>"Ignore Empty Tags"</font></h3>

If set to false, tags must point to at least one object

* default: false

<h3>TagList (input:string)<br><font size=2>"Tag List"</font></h3>

List of Tags from which to get objects to be configured

* default: <font color=#cc8888>(empty string)</font>

<h3>CurrVal (input:string)<br><font size=2>"Current value"</font></h3>

Value to use in the current iteration

* default: <font color=#cc8888>(empty string)</font>

<h3>Iteration (input:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<font color="red">MISSING JSON SAMPLE</font>

<h2>- UsedIn</h2>
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
</script># IteratorConfigPropertyValueCommand

<h3>Extends spirent.methodology.IteratorConfigCommand.</h3>

Configure the property for objects of a given type

<h2>- Properties</h2>

<h3>ClassName (input:string)<br><font size=2>"Class Name"</font></h3>

Name of the object's class

* default: <font color=#cc8888>(empty string)</font>

<h3>PropertyName (input:string)<br><font size=2>"Property Name"</font></h3>

Name of the property to configure

* default: <font color=#cc8888>(empty string)</font>

<h3>ObjectList (input:handle)<br><font size=2>"Object List"</font></h3>

List of objects to configure

* default: <font color=#cc8888>(empty)</font>

<h3>IgnoreEmptyTags (input:bool)<br><font size=2>"Ignore Empty Tags"</font></h3>

If set to false, tags must point to at least one object

* default: false

<h3>TagList (input:string)<br><font size=2>"Tag List"</font></h3>

List of Tags from which to get objects to be configured

* default: <font color=#cc8888>(empty string)</font>

<h3>CurrVal (input:string)<br><font size=2>"Current value"</font></h3>

Value to use in the current iteration

* default: <font color=#cc8888>(empty string)</font>

<h3>Iteration (input:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<h2>- UsedIn</h2>
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
</script># IteratorConfigRotateTrafficMixWeightsCommand

<h3>Extends spirent.methodology.IteratorConfigCommand.</h3>

Reconfigure the Traffic Mix's load weights by rotating the weights list to the right by RotationCount (or left by a negative count).

<h2>- Properties</h2>

<h3>ObjectList (input:handle)<br><font size=2>"Object List"</font></h3>

List of objects to configure

* default: <font color=#cc8888>(empty)</font>

<h3>IgnoreEmptyTags (input:bool)<br><font size=2>"Ignore Empty Tags"</font></h3>

If set to false, tags must point to at least one object

* default: false

<h3>TagList (input:string)<br><font size=2>"Tag List"</font></h3>

List of Tags from which to get objects to be configured

* default: <font color=#cc8888>(empty string)</font>

<h3>CurrVal (input:string)<br><font size=2>"Current value"</font></h3>

Value to use in the current iteration

* default: <font color=#cc8888>(empty string)</font>

<h3>Iteration (input:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<h2>- UsedIn</h2>
* ACL Performance Test


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
</script># IteratorConfigTrafficLoadCommand

<h3>Extends spirent.methodology.IteratorConfigCommand.</h3>

Configure the traffic load on a group of tagged streamblocks

<h2>- Properties</h2>

<h3>LoadUnit (input:u8)<br><font size=2>"Load Units"</font></h3>

Load Units

* default: PERCENT_LINE_RATE

		StreamBlock.EnumLoadUnit


<h3>ObjectList (input:handle)<br><font size=2>"Object List"</font></h3>

List of objects to configure

* default: <font color=#cc8888>(empty)</font>

<h3>IgnoreEmptyTags (input:bool)<br><font size=2>"Ignore Empty Tags"</font></h3>

If set to false, tags must point to at least one object

* default: false

<h3>TagList (input:string)<br><font size=2>"Tag List"</font></h3>

List of Tags from which to get objects to be configured

* default: <font color=#cc8888>(empty string)</font>

<h3>CurrVal (input:string)<br><font size=2>"Current value"</font></h3>

Value to use in the current iteration

* default: <font color=#cc8888>(empty string)</font>

<h3>Iteration (input:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<h2>- UsedIn</h2>
* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* ITU-T Y.1564 Service Configuration Test


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
</script># IteratorValidateCommand

Base Iterator Validate Command

<h2>- Properties</h2>

<h3>Iteration (input:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<h3>Verdict (output:bool)<br><font size=2>"Verdict"</font></h3>

Validate command's verdict

* default: True

<h2>- UsedIn</h2>
* Routing Multi-Protocol

* RFC 2544 Throughput Test

* ACL Performance Test


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
</script># L2L3LearningCommand

L2L3 Learning Command

<h2>- Properties</h2>

<h3>ObjectList (input:handle)<br><font size=2>"Object List"</font></h3>

List of port, stream block, host, router, or emulated device handles.

* default: 0

<h3>TagNameList (input:string)<br><font size=2>"Tag Name List"</font></h3>

List of tag names identifying port, stream block, host, router, or emulated device

* default: <font color=#cc8888>(empty string)</font>

<h3>EnableL2Learning (input:bool)<br><font size=2>"Enable L2 Learning"</font></h3>

Enable L2 Learning

* default: true

<h3>EnableL3Learning (input:bool)<br><font size=2>"Enable L3 Learning"</font></h3>

Enable L3 Learning

* default: true

<h3>L2LearningOption (input:u8)<br><font size=2>"L2 Learning Option"</font></h3>

L2LearningOption takes places on Tx, or Rx, or both Tx and Rx. Only used for L2 learning.

* default: TX_RX

		EnumL2LearningOption
		    TX_ONLY = 0
		    RX_ONLY = 1
		    TX_RX = 2


<h3>WaitForArpToFinish (input:bool)<br><font size=2>"Wait For Arp To Finish"</font></h3>

Wait for Arp to finish. Only used for L3 learning.

* default: true

<h3>ForceArp (input:bool)<br><font size=2>"Always Arp"</font></h3>

If Arp should always occur even if it is not required. Only used for L3 learning.

* default: true

<h3>VerifyArp (input:bool)<br><font size=2>"Verify Arp Status"</font></h3>

Verifiy if Arp resolved.

* default: true

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
</script># LoadTemplateCommand

<h3>Extends stak.StakGroupCommand.</h3>

Load an XML template into an StmTemplateConfig object

<h2>- Properties</h2>

<h3>CopiesPerParent (input:u32)<br><font size=2>"Number of copies to make per Target Tag object"</font></h3>

Number of copies of the template to make per Target Tag object

* default: 1

<h3>TargetTagList (input:string)<br><font size=2>"Target Tag List"</font></h3>

List of tags where the Source Tags will be appended.

* default: <font color=#cc8888>(empty string)</font>

<h3>TemplateXml (input:string)<br><font size=2>"XML Template String"</font></h3>

Template to use as a string

* default: <font color=#cc8888>(empty string)</font>

<h3>TemplateXmlFileName (input:inputFilePath)<br><font size=2>"XML Template File"</font></h3>

Template XML File Location

* default: <font color=#cc8888>(empty)</font>

<h3>TagPrefix (input:string)<br><font size=2>"Tag Prefix"</font></h3>

Prefix value prepended to all tags loaded by configuration

* default: <font color=#cc8888>(empty string)</font>

<h3>AutoExpandTemplate (input:bool)<br><font size=2>"Automatically Expand Template"</font></h3>

Expand template into EmulatedDevices, Streamblocks, etc.

* default: true

<h3>StmTemplateMix (input:handle)<br><font size=2>"Parent StmTemplateMix object"</font></h3>

Handle of an StmTemplateMix object to use for the parent of the created StmTemplateConfig.

* default: <font color=#cc8888>(empty)</font>

<h3>EnableLoadFromFileName (input:bool)<br><font size=2>"Enable XML Template File"</font></h3>

Load the XML from a Template File rather than the Template XML string parameter.

* default: true

<h3>StmTemplateConfig (output:handle)<br><font size=2>"XML container object (StmTemplateConfig)"</font></h3>

StmTemplateConfig container object

* default: <font color=#cc8888>(empty)</font>

<h2>- UsedIn</h2>
* L3 QoS DiffServ

* BGP Route Reflector Test

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* Widgets Test

* Basic Traffic Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* ACL Basic Test


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
</script># MergeTemplateCommand

Merges XML from a source string or file into the StmTemplateConfig container using source and target tags.

<h2>- Properties</h2>

<h3>StmTemplateConfig (input:handle)<br><font size=2>"StmTemplateConfig (from LoadTemplateCommand)"</font></h3>

StmTemplateConfig container object passed in from the LoadTemplateCommand

* default: <font color=#cc8888>(empty)</font>

<h3>SrcTagList (input:string)<br><font size=2>"Source Tag List"</font></h3>

List of tags from the XML Template String or File whose elements will be merged into the TemplateXml contained in the StmTemplateConfig

* default: <font color=#cc8888>(empty string)</font>

<h3>TargetTagList (input:string)<br><font size=2>"Target Tag List"</font></h3>

List of tags in the StmTemplateConfig's TemplateXml string where the Source Tag List's tagged elements will be inserted.

* default: <font color=#cc8888>(empty string)</font>

<h3>TagPrefix (input:string)<br><font size=2>"Tag Prefix"</font></h3>

Prefix value prepended to all merged tags loaded in the source XML

* default: <font color=#cc8888>(empty string)</font>

<h3>TemplateXml (input:string)<br><font size=2>"XML Template String"</font></h3>

String XML that will serve as a source

* default: <font color=#cc8888>(empty string)</font>

<h3>TemplateXmlFileName (input:inputFilePath)<br><font size=2>"XML Template File"</font></h3>

Template XML File Location that will serve as a source

* default: <font color=#cc8888>(empty)</font>

<h3>EnableLoadFromFileName (input:bool)<br><font size=2>"Enable XML Template File"</font></h3>

Load the XML from a Template File rather than the Template XML string parameter.

* default: true


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
</script># ModifyHandleListCommand

Modify a property of a BLL command that contains a list of handles

<h2>- Properties</h2>

<h3>BllCommandTagName (input:string)<br><font size=2>"Tag that identifies target BLL Command"</font></h3>

Name of the tag that the target BLL command will have a UserTag relation to.

* default: <font color=#cc8888>(empty string)</font>

<h3>PropertyName (input:string)<br><font size=2>"Property To Modify"</font></h3>

The property in the target BLL command that will have its contents modified.

* default: <font color=#cc8888>(empty string)</font>

<h3>TagList (input:string)<br><font size=2>"Tag List"</font></h3>

List of tags that will be expanded into BLL objects, then passed in to the command.  If the command already has handles, these handles will be appended to its list.

* default: <font color=#cc8888>(empty string)</font>

<h3>OverwriteProperty (input:bool)<br><font size=2>"Overwrite Property"</font></h3>

If set to true, will overwrite the property to modify.  If false, command will append.

* default: true

<h2>- UsedIn</h2>
* L3 QoS DiffServ

* BGP Route Reflector Test

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* Widgets Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ITU-T Y.1564 Microburst Test


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
</script># ModifyTemplatePropertyCommand

Modify an XML template across ports

<h2>- Properties</h2>

<h3>StmTemplateConfig (input:handle)<br><font size=2>"StmTemplateConfig"</font></h3>

StmTemplateConfig

* default: <font color=#cc8888>(empty)</font>

<h3>TagNameList (input:string)<br><font size=2>"Tag Name List"</font></h3>

Name of the Tag(s) referencing objects to modify in the template

* default: <font color=#cc8888>(empty string)</font>

<h3>PropertyList (input:string)<br><font size=2>"Property List"</font></h3>

List of property IDs (ie classname.property) to configure new values for.  Position in this list MUST map to position in the ValueList.

* default: <font color=#cc8888>(empty string)</font>

<h3>ValueList (input:string)<br><font size=2>"Value List"</font></h3>

List of values to configure.  Position in this list MUST map to position in the PropertyList.

* default: <font color=#cc8888>(empty string)</font>

<h2>- UsedIn</h2>
* L3 QoS DiffServ

* BGP Route Reflector Test

* ITU-T Y.1564 Service Configuration Test

* Widgets Test

* Basic Traffic Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Basic Test


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
</script># ObjectIteratorCommand

<h3>Extends spirent.methodology.IteratorCommand.</h3>

Object Iterator Command

<h2>- Properties</h2>

<h3>IterMode (input:u8)<br><font size=2>"Iteration Mode"</font></h3>

Iteration mode

* default: STEP

		EnumIterMode
		    STEP = 1
		    BINARY = 2


<h3>StepVal (input:double)<br><font size=2>"Step value"</font></h3>

Step value

* default: 10

<h3>ValueType (input:u8)<br><font size=2>"Value type"</font></h3>

Value type (list or range)

* default: RANGE

		EnumValueType
		    RANGE = 1
		    LIST = 2


<h3>ValueList (input:string)<br><font size=2>"List of values"</font></h3>

List of values to test

* default: <font color=#cc8888>(empty string)</font>

<h3>CurrIndex (state:u32)<br><font size=2>"Current Index"</font></h3>

Current list value's index

* default: 0

<h3>MinFail (state:double)<br><font size=2>"Minimum fail value"</font></h3>

Minimum fail value

* default: <font color=#cc8888>(empty)</font>

<h3>MaxPass (state:double)<br><font size=2>"Maximum pass value"</font></h3>

Maximum pass value

* default: <font color=#cc8888>(empty)</font>

<h3>IsConverged (output:bool)<br><font size=2>"Is Converged"</font></h3>

Did the iterator converge?

* default: false

<h3>ConvergedVal (output:string)<br><font size=2>"Converged Value"</font></h3>

Value the iterator converged on

* default: <font color=#cc8888>(empty string)</font>

<h3>BreakOnFail (input:bool)<br><font size=2>"Break on fail"</font></h3>

Break out of the test when an iteration fails

* default: false

<h3>MinVal (input:double)<br><font size=2>"Minimum value"</font></h3>

Minimum value

* default: 0

<h3>MaxVal (input:double)<br><font size=2>"Maximum value"</font></h3>

Maximum value

* default: 100

<h3>PrevIterVerdict (input:bool)<br><font size=2>"Previous iteration result"</font></h3>

Result of the previous iteration

* default: true

<h3>Iteration (state:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<h3>CurrVal (state:string)<br><font size=2>"Current value"</font></h3>

Value to use in the current iteration

* default: <font color=#cc8888>(empty string)</font>

<h3>ResetState (state:bool)<br><font size=2>"Reset State"</font></h3>

Reset state properties

* default: false

<h2>- UsedIn</h2>
* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

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
</script># RateIteratorCommand

<h3>Extends spirent.methodology.IteratorCommand.</h3>

Rate Iterator Command

<h2>- Properties</h2>

<h3>Resolution (input:double)<br><font size=2>"Resolution"</font></h3>

How close to get to the true value

* default: 1

<h3>ResolutionMode (input:u8)<br><font size=2>"Resolution Mode"</font></h3>

Resolution units

* default: PERCENT

		EnumResolutionMode
		    PERCENT = 1
		    ABSOLUTE = 2


<h3>RoundingResolution (input:double)<br><font size=2>"Rounding Resolution"</font></h3>

How to round the values used. 0 means no rounding.

* default: 0

<h3>MinFail (state:double)<br><font size=2>"Minimum fail value"</font></h3>

Minimum fail value

* default: <font color=#cc8888>(empty)</font>

<h3>MaxPass (state:double)<br><font size=2>"Maximum pass value"</font></h3>

Maximum pass value

* default: <font color=#cc8888>(empty)</font>

<h3>IsConverged (output:bool)<br><font size=2>"Is Converged"</font></h3>

Did the iterator converge?

* default: false

<h3>ConvergedVal (output:string)<br><font size=2>"Converged Value"</font></h3>

Value the iterator converged on

* default: <font color=#cc8888>(empty string)</font>

<h3>BreakOnFail (input:bool)<br><font size=2>"Break on fail"</font></h3>

Break out of the test when an iteration fails

* default: false

<h3>MinVal (input:double)<br><font size=2>"Minimum value"</font></h3>

Minimum value

* default: 0

<h3>MaxVal (input:double)<br><font size=2>"Maximum value"</font></h3>

Maximum value

* default: 100

<h3>PrevIterVerdict (input:bool)<br><font size=2>"Previous iteration result"</font></h3>

Result of the previous iteration

* default: true

<h3>Iteration (state:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<h3>CurrVal (state:string)<br><font size=2>"Current value"</font></h3>

Value to use in the current iteration

* default: <font color=#cc8888>(empty string)</font>

<h3>ResetState (state:bool)<br><font size=2>"Reset State"</font></h3>

Reset state properties

* default: false

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
</script># ResetRotateTrafficMixWeightsCommand

Configure the TrafficProfile's frame size

<h2>- Properties</h2>

<h3>ObjectList (input:handle)<br><font size=2>"Object List"</font></h3>

List of objects to configure

* default: <font color=#cc8888>(empty)</font>

<h3>TrafficMixTagList (input:string)<br><font size=2>"Traffic Mix Tag List"</font></h3>

List of Tag names to identify the Traffic Mix objects.

* default: <font color=#cc8888>(empty string)</font>

<h2>- UsedIn</h2>
* ACL Performance Test


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
</script># RunPyScriptCommand

Run a python script.

<h2>- Properties</h2>

<h3>ScriptFilename (input:inputFilePath)<br><font size=2>"Python script file"</font></h3>

The python script file (without the py extension).

* default: <font color=#cc8888>(empty)</font>

<h3>MethodName (input:string)<br><font size=2>"Method within the script"</font></h3>

The python script method to run.

* default: run

<h3>TagName (input:string)<br><font size=2>"Name of the tag associated with the target object(s)"</font></h3>

Name of the tag used to form a collection of objects for the script to act on.

* default: <font color=#cc8888>(empty string)</font>

<h3>Params (input:string)<br><font size=2>"A string for the script"</font></h3>

A string parameter that is passed to the script to work with.

* default: <font color=#cc8888>(empty string)</font>

<h3>ErrorMsg (output:string)<br><font size=2>"Error Message"</font></h3>

Holds the last error message recorded by the command.

* default: <font color=#cc8888>(empty string)</font>

<h2>- UsedIn</h2>
* L3 QoS DiffServ

* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* ACL Basic Test

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
</script># StabilityBackoffIteratorCommand

<h3>Extends spirent.methodology.IteratorCommand.</h3>

Stability Backoff Iterator (reverse iteration from a maximum value while repeating each test value some number of times for stability)

<h2>- Properties</h2>

<h3>StepVal (input:double)<br><font size=2>"Step value"</font></h3>

Amount to step backwards by

* default: 10

<h3>RepeatCount (input:u32)<br><font size=2>"Step value"</font></h3>

Number of times to repeat an iteration

* default: 5

<h3>SuccessPercent (input:double)<br><font size=2>"Success Percent"</font></h3>

Number of times a repeated value has to pass to be considered stable

* default: 100

<h3>ValueType (input:u8)<br><font size=2>"Value type"</font></h3>

Value type (list or range)

* default: RANGE

		EnumValueType
		    RANGE = 1
		    LIST = 2


<h3>ValueList (input:string)<br><font size=2>"List of values"</font></h3>

List of values to test

* default: <font color=#cc8888>(empty string)</font>

<h3>CurrIndex (state:u32)<br><font size=2>"Current Index"</font></h3>

Current list value's index

* default: 0

<h3>MinFail (state:double)<br><font size=2>"Minimum fail value"</font></h3>

Minimum fail value

* default: <font color=#cc8888>(empty)</font>

<h3>MaxPass (state:double)<br><font size=2>"Maximum pass value"</font></h3>

Maximum pass value

* default: <font color=#cc8888>(empty)</font>

<h3>SuccessCount (state:u32)<br><font size=2>"Success Count"</font></h3>

Number of successful trials

* default: 0

<h3>TrialNum (state:u32)<br><font size=2>"Trial Number"</font></h3>

Trial number for a particular test value

* default: 0

<h3>StableValue (output:string)<br><font size=2>"Stable value"</font></h3>

Stable value

* default: 0

<h3>FoundStableValue (output:bool)<br><font size=2>"Found a stable value"</font></h3>

Flag indicating a stable value was found

* default: false

<h3>BreakOnFail (input:bool)<br><font size=2>"Break on fail"</font></h3>

Break out of the test when an iteration fails

* default: false

<h3>MinVal (input:double)<br><font size=2>"Minimum value"</font></h3>

Minimum value

* default: 0

<h3>MaxVal (input:double)<br><font size=2>"Maximum value"</font></h3>

Maximum value

* default: 100

<h3>PrevIterVerdict (input:bool)<br><font size=2>"Previous iteration result"</font></h3>

Result of the previous iteration

* default: true

<h3>Iteration (state:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<h3>CurrVal (state:string)<br><font size=2>"Current value"</font></h3>

Value to use in the current iteration

* default: <font color=#cc8888>(empty string)</font>

<h3>ResetState (state:bool)<br><font size=2>"Reset State"</font></h3>

Reset state properties

* default: false

<h2>- UsedIn</h2>
* ACL Performance Test


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
</script># StartOfTestCommand

Initializes test results

<h2>- Properties</h2>

<h2>- UsedIn</h2>
* L3 QoS DiffServ

* BGP Route Reflector Test

* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* Widgets Test

* Basic Traffic Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* ACL Basic Test

* ITU-T Y.1564 Microburst Test

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
</script># TaggedLinkCreateCommand

Create Links With Tagged Objects

<h2>- Properties</h2>

<h3>LinkType (input:string)<br><font size=2>"Link Type"</font></h3>

Name Link Created between objects

* default: <font color=#cc8888>(empty string)</font>

<h3>SrcObjTag (input:string)<br><font size=2>"Source Object Tag"</font></h3>

Tag used for Source (Back) Objects

* default: <font color=#cc8888>(empty string)</font>

<h3>SrcIfTag (input:string)<br><font size=2>"Source Interface Tag"</font></h3>

Tag used for Source (Back) Interface Objects

* default: <font color=#cc8888>(empty string)</font>

<h3>DstObjTag (input:string)<br><font size=2>"Destination Object Tag"</font></h3>

Tag used for Destination (Front) Objects

* default: <font color=#cc8888>(empty string)</font>

<h3>DstIfTag (input:string)<br><font size=2>"Destination Interface Tag"</font></h3>

Tag used for Destination (Front) Interface Objects

* default: <font color=#cc8888>(empty string)</font>

<h3>LinkPattern (input:u8)<br><font size=2>"Link Distribution Pattern"</font></h3>

Link Distribution Pattern

* default: PAIR

		EnumLinkPattern
		    PAIR = 0
		    BACKBONE = 1
		    INTERLEAVED = 2


<h3>LinkTag (input:string)<br><font size=2>"Tag for newly-created Link Objects"</font></h3>

If not blank, tag used with new link objects 

* default: <font color=#cc8888>(empty string)</font>

<h3>LinkList (output:handle)<br><font size=2>"List of created Link objects"</font></h3>

Contains list of handles for links created

* default: <font color=#cc8888>(empty)</font>


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
</script># TaggedObjectsIteratorCommand

<h3>Extends spirent.methodology.IteratorCommand.</h3>

Tagged Objects Iterator Command

<h2>- Properties</h2>

<h3>ObjectOrder (input:u8)<br><font size=2>"Iteration Mode"</font></h3>

Order of tagged objects

* default: SCALAR

		EnumObjectOrder
		    SCALAR = 1
		    TUPLE = 2


<h3>TagNameList (input:string)<br><font size=2>"List of Tag Names"</font></h3>

Obtain objects from named tags

* default: <font color=#cc8888>(empty string)</font>

<h3>BreakOnFail (input:bool)<br><font size=2>"Break on fail"</font></h3>

Break out of the test when an iteration fails

* default: false

<h3>MinVal (input:double)<br><font size=2>"Minimum value"</font></h3>

Minimum value

* default: 0

<h3>MaxVal (input:double)<br><font size=2>"Maximum value"</font></h3>

Maximum value

* default: 100

<h3>PrevIterVerdict (input:bool)<br><font size=2>"Previous iteration result"</font></h3>

Result of the previous iteration

* default: true

<h3>Iteration (state:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<h3>CurrVal (state:string)<br><font size=2>"Current value"</font></h3>

Value to use in the current iteration

* default: <font color=#cc8888>(empty string)</font>

<h3>ResetState (state:bool)<br><font size=2>"Reset State"</font></h3>

Reset state properties

* default: false

<h2>- UsedIn</h2>
* ITU-T Y.1564 CBS and EBS Burst Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 Service Performance Test


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
</script># TagObjectConfigCommand

<h3>Extends spirent.methodology.IteratorConfigCommand.</h3>

Set Tag to only point to specified object handle(s)

<h2>- Properties</h2>

<h3>TagNameList (input:string)<br><font size=2>"Tag Name List"</font></h3>

List of Tags used to tag objects specified

* default: <font color=#cc8888>(empty string)</font>

<h3>ObjectList (input:handle)<br><font size=2>"Object List"</font></h3>

List of objects to configure

* default: <font color=#cc8888>(empty)</font>

<h3>IgnoreEmptyTags (input:bool)<br><font size=2>"Ignore Empty Tags"</font></h3>

If set to false, tags must point to at least one object

* default: false

<h3>TagList (input:string)<br><font size=2>"Tag List"</font></h3>

List of Tags from which to get objects to be configured

* default: <font color=#cc8888>(empty string)</font>

<h3>CurrVal (input:string)<br><font size=2>"Current value"</font></h3>

Value to use in the current iteration

* default: <font color=#cc8888>(empty string)</font>

<h3>Iteration (input:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<h2>- UsedIn</h2>
* ITU-T Y.1564 CBS and EBS Burst Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 Service Performance Test


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
</script># ValidateRouterUpCommand

<h3>Extends spirent.methodology.IteratorValidateCommand.</h3>

Validate Router Up

<h2>- Properties</h2>

<h3>Iteration (input:u32)<br><font size=2>"Iteration"</font></h3>

Iteration number

* default: 0

<h3>Verdict (output:bool)<br><font size=2>"Verdict"</font></h3>

Validate command's verdict

* default: True


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
</script># VerifyDbQueryCommand

<h3>Extends spirent.methodology.VerifySingleBaseCommand.</h3>

Verify that an SqlQuery yields a row count that meets the specified limits.

<h2>- Properties</h2>

<h3>SqlQuery (input:string)<br><font size=2>"Sql Query"</font></h3>

Sql Query

* default: <font color=#cc8888>(empty string)</font>

<h3>OperationType (input:u8)<br><font size=2>"Operation Type"</font></h3>

Comparision operator

* default: GREATER_THAN

		spirent.methodology.ResultBaseCommand.EnumComparisonOperator


<h3>RowCount (input:u64)<br><font size=2>"Row Count"</font></h3>

Row count to compare to SQL query yield based on OperationType. Valid for all OperationType values except Between.

* default: 0

<h3>MinRowCount (input:u64)<br><font size=2>"Min Row Count (Inclusive)"</font></h3>

Minimum acceptable row count when OperationType is Between.

* default: 0

<h3>MaxRowCount (input:u64)<br><font size=2>"Max Row Count (Inclusive)"</font></h3>

Maximum acceptable row count when OperationType is Between.

* default: 0

<h3>UseMultipleResultsDatabases (input:bool)<br><font size=2>"Has Multiple Results Databases"</font></h3>

Used when there are multiple results databases (SaveResults LoopMode = Append). All active results databases will be queried. If set to True and only one results database exists (SaveResults LoopMode = Overwrite), an error will occur.

* default: false

<h3>UseSummary (input:bool)<br><font size=2>"Use the summery db only"</font></h3>

Use the summary db instead of iteration dbs. Only valid if UseMultipleResultsDatabases is False.

* default: false

<h3>DisplayName (input:string)<br><font size=2>"Display Name"</font></h3>

Title to display for this result section in the report file.

* default: <font color=#cc8888>(empty string)</font>

<h3>PassedVerdictExplanation (input:string)<br><font size=2>"Passed Verdict Explanation"</font></h3>

Verdict explanation if command passes.

* default: <font color=#cc8888>(empty string)</font>

<h3>FailedVerdictExplanation (input:string)<br><font size=2>"Failed Verdict Explanation"</font></h3>

Verdict explanation if command fails.

* default: <font color=#cc8888>(empty string)</font>

<h2>- UsedIn</h2>
* L3 QoS DiffServ

* BGP Route Reflector Test

* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* Widgets Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* ACL Basic Test

* ITU-T Y.1564 Microburst Test

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
</script># VerifyDynamicResultViewDataCommand

<h3>Extends spirent.methodology.VerifySingleBaseCommand.</h3>

Verify that DRV yields a result count that meets the specified limits.

<h2>- Properties</h2>

<h3>DynamicResultViewName (input:string)<br><font size=2>"Dynamic Result View Name"</font></h3>

Dynamic Result View Name.

* default: <font color=#cc8888>(empty string)</font>

<h3>OperationType (input:u8)<br><font size=2>"Operation Type"</font></h3>

Comparision operator

* default: GREATER_THAN

		spirent.methodology.ResultBaseCommand.EnumComparisonOperator


<h3>ResultCount (input:u64)<br><font size=2>"Result Count"</font></h3>

Result count to compare to DRV yield based on OperationType. Valid for all OperationType values except Between.

* default: 0

<h3>MinResultCount (input:u64)<br><font size=2>"Min Result Count (Inclusive)"</font></h3>

Minimum acceptable result count when OperationType is Between.

* default: 0

<h3>MaxResultCount (input:u64)<br><font size=2>"Max Result Count (Inclusive)"</font></h3>

Maximum acceptable result count when OperationType is Between.

* default: 0

<h3>DisplayName (input:string)<br><font size=2>"Display Name"</font></h3>

Title to display for this result section in the report file.

* default: <font color=#cc8888>(empty string)</font>

<h3>PassedVerdictExplanation (input:string)<br><font size=2>"Passed Verdict Explanation"</font></h3>

Verdict explanation if command passes.

* default: <font color=#cc8888>(empty string)</font>

<h3>FailedVerdictExplanation (input:string)<br><font size=2>"Failed Verdict Explanation"</font></h3>

Verdict explanation if command fails.

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
</script># VerifyMultipleDbQueryCommand

<h3>Extends spirent.methodology.VerifyMultiBaseCommand.</h3>

Verify that each query in a list of SqlQueries yields row count = 0.

<h2>- Properties</h2>

<h3>SqlQueryList (input:string)<br><font size=2>"Sql Query List"</font></h3>

A list of 1 or more SQL queries.

* default: <font color=#cc8888>(empty string)</font>

<h3>UseMultipleResultsDatabases (input:bool)<br><font size=2>"Has Multiple Results Databases"</font></h3>

Used when there are multiple results databases (SaveResults LoopMode = Append). All active results databases will be queried. If set to True and only one results database exists (SaveResults LoopMode = Overwrite), an error will occur.

* default: false

<h3>UseSummary (input:bool)<br><font size=2>"Use Summary Database Only"</font></h3>

Use the summary database instead of the iteration databases. Only valid if UseMultipleResultsDatabases is False.

* default: false

<h3>DisplayNameList (input:string)<br><font size=2>"Display Name List"</font></h3>

Title to display for this result section in the report file. Maps 1-1 with validation query/configuration.

* default: <font color=#cc8888>(empty string)</font>

<h3>PassedVerdictExplanationList (input:string)<br><font size=2>"Passed Verdict Explanation List"</font></h3>

Verdict explanation if command passes. Maps 1-1 with validation query/configuration.

* default: <font color=#cc8888>(empty string)</font>

<h3>FailedVerdictExplanationList (input:string)<br><font size=2>"Failed Verdict Explanation List"</font></h3>

Verdict explanation if command fails. Maps 1-1 with validation query/configuration.

* default: <font color=#cc8888>(empty string)</font>

<h2>- UsedIn</h2>
* L3 QoS DiffServ

* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* ITU-T Y.1564 Microburst Test

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
</script># WaitForPropertyValueCommand

Wait for an object's property to reach a certain value

<h2>- Properties</h2>

<h3>ParentList (input:handle)<br><font size=2>"Parent List"</font></h3>

List of parent objects to wait for property value on

* default: <font color=#cc8888>(empty)</font>

<h3>ObjectClassName (input:string)<br><font size=2>"Object Class Name"</font></h3>

Object Class Name

* default: <font color=#cc8888>(empty string)</font>

<h3>PropertyName (input:string)<br><font size=2>"Property Name"</font></h3>

Name of the Property to wait for

* default: <font color=#cc8888>(empty string)</font>

<h3>PropertyValue (input:string)<br><font size=2>"Property Value"</font></h3>

Name of the value to wait for

* default: 0

<h3>PropertyValueType (input:u8)<br><font size=2>"Property Value Type"</font></h3>

Property Value Type

* default: 0

		EnumPropertyValueType
		    NUMBER = 0
		    BOOL = 1
		    STRING = 2
		    ENUM = 3


<h3>OperationType (input:u8)<br><font size=2>"Operation Type"</font></h3>

Name of the value to wait for

* default: 0

		EnumOperationType
		    EQUALS = 0
		    NOT_EQUALS = 1
		    GREATER_THAN = 2
		    LESS_THAN = 3
		    GREATER_THAN_OR_EQUALS = 4
		    LESS_THAN_OR_EQUALS = 5


<h3>PollInterval (input:u32)<br><font size=2>"Poll Interval"</font></h3>

How often to poll state result in seconds

* default: 10

<h3>MaxWaitTime (input:u32)<br><font size=2>"Maximum Wait Time"</font></h3>

Maximum amount of time to wait for state change in seconds

* default: 10

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