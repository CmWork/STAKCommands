# RateIteratorCommand

Rate Iterator Command

<font size="2">File Reference: stc_testmethodology.xml</font>

## Properties

### IsConverged: "Is Converged" (output:bool)

Did the iterator converge?

* default - false
### RoundingResolution: "Rounding Resolution" (input:double)

How to round the values used. 0 means no rounding.

* default - 0
### ConvergedVal: "Converged Value" (output:string)

Value the iterator converged on

* default - 
### MaxPass: "Maximum pass value" (state:double)

Maximum pass value

* default - 
### ResolutionMode: "Resolution Mode" (input:u8)

Resolution units

* default - PERCENT
### MinFail: "Minimum fail value" (state:double)

Minimum fail value

* default - 
### Resolution: "Resolution" (input:double)

How close to get to the true value

* default - 1
## UsedIn
* RFC 2544 Throughput Test

