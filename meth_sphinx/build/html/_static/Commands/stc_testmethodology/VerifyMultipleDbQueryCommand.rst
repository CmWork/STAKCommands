# VerifyMultipleDbQueryCommand

Verify that each query in a list of SqlQueries yields row count = 0.

<font size="2">File Reference: stc_testmethodology.xml</font>

## Properties

### UseMultipleResultsDatabases: "Has Multiple Results Databases" (input:bool)

Used when there are multiple results databases (SaveResults LoopMode = Append). All active results databases will be queried. If set to True and only one results database exists (SaveResults LoopMode = Overwrite), an error will occur.

* default - false
### SqlQueryList: "Sql Query List" (input:string)

A list of 1 or more SQL queries.

* default - 
### UseSummary: "Use Summary Database Only" (input:bool)

Use the summary database instead of the iteration databases. Only valid if UseMultipleResultsDatabases is False.

* default - false
## UsedIn
* L3 QoS DiffServ

* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* ITU-T Y.1564 Microburst Test

* RFC 2544 Throughput Test

