# CreateMethodologyChartCommand

Export Chart

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### ChartTemplateJsonFileName: "Chart Template File" (input:inputFilePath)

Chart template file in JSON format. May use one of the provided basic templates: Line_Template.json and Column_Template.json.

* default - Line_Template.json
### Title: "Chart Title" (input:string)

Title displayed at the top of the chart.

* default - Result Node Param Handles
### Series: "Series' Data" (input:string)

Set of data to be plotted on the chart specified as a list of strings or SQL queries. Each list element is a series. The string format to plot a single data type is: 1, 2, 3, 4. Plotting two data types is: [1, 1], [2, 2].

* default - 
### YAxisTitle: "Y Axis Title" (input:string)

Title displayed along the Y axis.

* default - Handle
### XAxisTitle: "X Axis Title" (input:string)

Title displayed along the X axis.

* default - Id
### TemplateModifier: "Template Modifier" (input:string)

Modify chart properties by specifying a string in JSON format that will be appended to the result file. Specified properties will be merged with and overwrite any existing properies in the chart template file. Follows the HighCharts API. Ex. {"yAxis": {"title": {"text": "Modified Label"}}} SQL Queries can be inserted to the JSON string by delimiting the queries with {{ and }}.

* default - {"series":[{"name": "Handles"}]}
### SrcDatabase: "Source Database" (input:u8)

Select source database(s) to execute the Sql queries.

* default - SUMMARY
### XAxisCategories: "X Axis Categories" (input:string)

X axis categories specified as a list of strings or SQL queries. Used to label the tick marks along the X axis.

* default - 
### YAxisCategories: "Y Axis Categories" (input:string)

Y axis categories specified as a list of strings or SQL queries. Used to label the tick marks along the Y axis.

* default - 
## UsedIn
* Routing Multi-Protocol

