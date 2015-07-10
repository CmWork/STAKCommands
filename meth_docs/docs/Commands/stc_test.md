# RateIteratorCommand

Rate Iterator Command

<h2>- Properties</h2>

<h3>IsConverged: "Is Converged" (output:bool)</h3>

Did the iterator converge?

* default - false

<h3>RoundingResolution: "Rounding Resolution" (input:double)</h3>

How to round the values used. 0 means no rounding.

* default - 0

<h3>ConvergedVal: "Converged Value" (output:string)</h3>

Value the iterator converged on

* default - 

<h3>MaxPass: "Maximum pass value" (state:double)</h3>

Maximum pass value

* default - 

<h3>ResolutionMode: "Resolution Mode" (input:u8)</h3>

Resolution units

* default - PERCENT

<h3>MinFail: "Minimum fail value" (state:double)</h3>

Minimum fail value

* default - 

<h3>Resolution: "Resolution" (input:double)</h3>

How close to get to the true value

* default - 1

<h2>- UsedIn</h2>
* RFC 2544 Throughput Test

# ObjectIteratorCommand

Object Iterator Command

<h2>- Properties</h2>

<h3>MaxPass: "Maximum pass value" (state:double)</h3>

Maximum pass value

* default - 

<h3>ValueType: "Value type" (input:u8)</h3>

Value type (list or range)

* default - RANGE

<h3>CurrIndex: "Current Index" (state:u32)</h3>

Current list value's index

* default - 0

<h3>IsConverged: "Is Converged" (output:bool)</h3>

Did the iterator converge?

* default - false

<h3>ValueList: "List of values" (input:string)</h3>

List of values to test

* default - 

<h3>MinFail: "Minimum fail value" (state:double)</h3>

Minimum fail value

* default - 

<h3>StepVal: "Step value" (input:double)</h3>

Step value

* default - 10

<h3>ConvergedVal: "Converged Value" (output:string)</h3>

Value the iterator converged on

* default - 

<h3>IterMode: "Iteration Mode" (input:u8)</h3>

Iteration mode

* default - STEP

<h2>- UsedIn</h2>
* Routing Multi-Protocol

* ITU-T Y.1564 Service Performance Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 CBS and EBS Burst Test

* ACL Performance Test

* RFC 2544 Throughput Test

