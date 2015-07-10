# StabilityBackoffIteratorCommand

Stability Backoff Iterator (reverse iteration from a maximum value while repeating each test value some number of times for stability)

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### MaxPass: "Maximum pass value" (state:double)

Maximum pass value

* default - 
### RepeatCount: "Step value" (input:u32)

Number of times to repeat an iteration

* default - 5
### ValueType: "Value type" (input:u8)

Value type (list or range)

* default - RANGE
### TrialNum: "Trial Number" (state:u32)

Trial number for a particular test value

* default - 0
### CurrIndex: "Current Index" (state:u32)

Current list value's index

* default - 0
### ValueList: "List of values" (input:string)

List of values to test

* default - 
### MinFail: "Minimum fail value" (state:double)

Minimum fail value

* default - 
### FoundStableValue: "Found a stable value" (output:bool)

Flag indicating a stable value was found

* default - false
### StableValue: "Stable value" (output:string)

Stable value

* default - 0
### StepVal: "Step value" (input:double)

Amount to step backwards by

* default - 10
### SuccessCount: "Success Count" (state:u32)

Number of successful trials

* default - 0
### SuccessPercent: "Success Percent" (input:double)

Number of times a repeated value has to pass to be considered stable

* default - 100
## UsedIn
* ACL Performance Test

