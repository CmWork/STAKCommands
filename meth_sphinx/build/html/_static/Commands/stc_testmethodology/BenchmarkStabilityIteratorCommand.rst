# BenchmarkStabilityIteratorCommand

Discrete step size binary or step search followed by stability test with backoff

<font size="2">File Reference: stc_testmethodology.xml</font>

## Properties

### SearchMinFail: "Minimum fail value" (state:double)

Minimum failing value encountered during search

* default - 
### IsConverged: "Is Converged" (output:bool)

Did the iterator converge?

* default - false
### SearchIteration: "Goal-seeking Test Iteration Number" (state:u32)

Iteration number used during goal-seek testing

* default - 0
### EnableStabilityBackoff: "Enable Stability Backoff" (input:bool)

Enable stability backoff iteration once a converged value is found.  If false, iteration will end once a converged value is found.

* default - true
### RepeatCount: "Repeat Count" (input:u32)

Number of times to repeat an iteration

* default - 5
### ValueType: "Value type" (input:u8)

Value type (list or range)

* default - RANGE
### StabilityIteration: "Stability Test Iteration Number" (state:u32)

Iteration number used during stability testing

* default - 0
### CurrIndex: "Current Index" (state:u32)

Current list value's index

* default - 0
### FoundStableValue: "Found a stable value" (output:bool)

Flag indicating a stable value was found

* default - false
### StabilitySuccessCount: "Stability Success Count" (state:u32)

Number of successful trials in a iteration during stability testing

* default - 0
### SearchMaxPass: "Maximum pass value" (state:double)

Maximum passing value encountered during search

* default - 
### ValueList: "List of values" (input:string)

List of values to test

* default - 
### IterState: "Iterator state" (state:u8)

Specifies what part of the search the iterator is in (goal-seeking or stability backoff)

* default - SEARCH
### StabilityTrialNum: "Stability Test Trial Number" (state:u32)

Trial number for a particular test value during stability testing

* default - 0
### StableValue: "Stable value" (output:string)

Stable value

* default - 0
### StepVal: "Step value" (input:double)

Step value

* default - 10
### ConvergedVal: "Converged Value" (output:string)

Value the iterator converged on

* default - 
### SuccessPercent: "Success Percent" (input:double)

Number of times a repeated value has to pass to be considered stable

* default - 100
### IterMode: "Iteration Mode" (input:u8)

Iteration mode

* default - STEP
## UsedIn
* Routing Multi-Protocol

