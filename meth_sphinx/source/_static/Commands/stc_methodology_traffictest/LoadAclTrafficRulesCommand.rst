# LoadAclTrafficRulesCommand

Import an Access Control List traffic mix rules file and generate the stream blocks from the rules.

<font size="2">File Reference: stc_methodology_traffictest.xml</font>

## Properties

### RulesFileName: "Rules File Name" (input:inputFilePath)

File name and path to the rules file to import.

* default - 
### StreamsPerRule: "Streams Per Rule" (input:u32)

The number of streams to create per rule.

* default - 1
### ConformToAccept: "Conform To Accept" (input:bool)

If true, the packet information is formed in conformity with the ACCEPT rules and non-conformity with the DENY rules,  thus the packets are expected to pass through the DUT. If false, then the packet information will conform with DENY and not with  ACCEPT, thus the packets are expected to be blocked by the DUT.

* default - false
## UsedIn
* ACL Performance Test

