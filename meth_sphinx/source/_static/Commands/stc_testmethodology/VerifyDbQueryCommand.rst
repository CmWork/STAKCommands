# VerifyDbQueryCommand

Verify that an SqlQuery yields a row count that meets the specified limits.

<font size="2">File Reference: stc_testmethodology.xml</font>

## Properties

### OperationType: "Operation Type" (input:u8)

Comparision operator

* default - GREATER_THAN
### MaxRowCount: "Max Row Count (Inclusive)" (input:u64)

Maximum acceptable row count when OperationType is Between.

* default - 0
### SqlQuery: "Sql Query" (input:string)

Sql Query

* default - 
### RowCount: "Row Count" (input:u64)

Row count to compare to SQL query yield based on OperationType. Valid for all OperationType values except Between.

* default - 0
### UseMultipleResultsDatabases: "Has Multiple Results Databases" (input:bool)

Used when there are multiple results databases (SaveResults LoopMode = Append). All active results databases will be queried. If set to True and only one results database exists (SaveResults LoopMode = Overwrite), an error will occur.

* default - false
### MinRowCount: "Min Row Count (Inclusive)" (input:u64)

Minimum acceptable row count when OperationType is Between.

* default - 0
### UseSummary: "Use the summery db only" (input:bool)

Use the summary db instead of iteration dbs. Only valid if UseMultipleResultsDatabases is False.

* default - false
## UsedIn
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

