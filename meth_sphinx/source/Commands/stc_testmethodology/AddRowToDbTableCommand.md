# AddRowToDbTableCommand

Add queried results to a new or existing table.

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### SqlQuery: "Source Data Sql Query" (input:string)

Sql query for source data. Queried results shall be populated in new or existing table specified in Create Table Sql Statement field. The number of columns in the query must match the number of columns in the table.

* default - SELECT Id, CreatedTime From DataSet
### DstDatabase: "Destination Database" (input:u8)

Select destination database to create new table.

* default - SUMMARY
### SrcDatabase: "Source Database" (input:u8)

Select source database(s) to execute Sql query.

* default - ALL_ITERATION
### SqlCreateTable: "Create Table Sql Statement" (input:string)

Specify a table name for an existing destination table or a Create Table Sql statement for a new destination table. If the table exists, a new one shall not be created.

* default - CREATE TABLE NewTableName ('Column1' INTEGER, 'Column2' TIMESTAMP)
## UsedIn
* RFC 2544 Throughput Test

* Routing Multi-Protocol

