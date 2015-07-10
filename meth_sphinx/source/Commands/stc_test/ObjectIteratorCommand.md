# ObjectIteratorCommand

Object Iterator Command

<font size="2">File Reference: stc_test.xml</font>

<text>Properties</text>

### MaxPass: "Maximum pass value" (state:double)

Maximum pass value

* default - 
### ValueType: "Value type" (input:u8)

Value type (list or range)

* default - RANGE
### CurrIndex: "Current Index" (state:u32)

Current list value's index

* default - 0
### IsConverged: "Is Converged" (output:bool)

Did the iterator converge?

* default - false
### ValueList: "List of values" (input:string)

List of values to test

* default - 
### MinFail: "Minimum fail value" (state:double)

Minimum fail value

* default - 
### StepVal: "Step value" (input:double)

Step value

* default - 10
### ConvergedVal: "Converged Value" (output:string)

Value the iterator converged on

* default - 
### IterMode: "Iteration Mode" (input:u8)

Iteration mode

* default - STEP
## UsedIn
* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* RFC 2544 Throughput Test

