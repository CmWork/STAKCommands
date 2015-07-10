# ExportDbChartCommand

Export Chart

<font size="2">File Reference: stc_testmethodology.xml</font>

## Properties

### CustomModifier: "Custom Modifier" (input:string)

JSON string that will be appended to the JSON result file which is used to modify chart properties. Follows HighCharts API. Ex. {"yAxis": {"title": {"text": "Modified Label"}}} SQL Queries can be inserted to the JSON string by delimiting the queries with {{ and }}

* default - 
### ChartTemplateJsonFileName: "Chart Template File" (input:inputFilePath)

Chart Template JSON File Location

* default - 
### UseSummary: "Use the summery db only" (input:bool)

Use the summary db instead of iteration dbs. Only valid if UseMultipleResultsDatabases is False.

* default - false
### Title: "Chart Title" (input:string)

Chart Title

* default - My Chart
### Series: "Series' Data" (input:string)

Set of data to be plotted on the chart (can be given as strings or SQL queries) Ex. String format for SeriesDataType(Single): 1, 2, 3, 4 SeriesDataType(Pair): [1, 1], [2, 2]

* default - 
### YAxisTitle: "Y Axis Title" (input:string)

Y Axis Title

* default - My Y Axis
### XAxisTitle: "X Axis Title" (input:string)

X Axis Title

* default - My X Axis
### UseMultipleResultsDatabases: "Has Multiple Results Databases" (input:bool)

Used when there are multiple results databases (SaveResults LoopMode = Append). All active results databases will be queried. If set to True and only one results database exists (SaveResults LoopMode = Overwrite), an error will occur.

* default - false
### SeriesDataType: "Series Data Type" (input:u8)

Series data can be given as a single or pair type. SINGLE = only Y values, X values are calculated automaticatlly. PAIR = [x,y] value pairs

* default - SINGLE
### XAxisCategories: "X Axis Categories" (input:string)

X Axis Categories (can be a string or SQL query). Used to label the tick marks along the X axis

* default - 
### YAxisCategories: "Y Axis Categories" (input:string)

Y Axis Categories (can be a string or SQL query). Used to label the tick marks along the Y axis

* default - 
## UsedIn
* ITU-T Y.1564 Microburst Test

* BGP Route Reflector Test

* Widgets Test

