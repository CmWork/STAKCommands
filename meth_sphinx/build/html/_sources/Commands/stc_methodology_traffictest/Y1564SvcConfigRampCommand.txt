# Y1564SvcConfigRampCommand

Configure Y1564 Service Configuration Ramp Test

<font size="2">File Reference: stc_methodology_traffictest.xml</font>

## Properties

### ExpMaxLatency: "Maximum Latency Threshold (ms)" (input:double)

Maximum Latency Threshold (ms)

* default - 1.0
### ExpPktLossCount: "Packet Loss Count Threshold" (input:u64)

Packet Loss Count Threshold

* default - 0
### ExpRfc4689AvgJitter: "RFC4689 Average Jitter Threshold (ms)" (input:double)

RFC4689 Average Jitter Threshold (ms)

* default - 0.05
### StartBw: "Starting Bandwidth" (input:double)

Starting Bandwidth

* default - 10.0
### ExpMaxOopCount: "Maximum Out of Order Packet Count Threshold" (input:u64)

Maximum Out of Order Packet Count Threshold

* default - 0
### ExpMaxLatePktCount: "Maximum Late Packet Count Threshold" (input:u64)

Maximum Late Packet Count Threshold

* default - 0
### CirBw: "Committed Information Rate (CIR) Bandwidth" (input:double)

Committed Information Rate (CIR) Bandwidth

* default - 20.0
### ExpMaxJitter: "Maximum Jitter Threshold (ms)" (input:double)

Maximum Jitter Threshold (ms)

* default - 0.2
### EirBw: "Excess Information Rate (EIR) Bandwidth" (input:double)

Excess Information Rate (EIR) Bandwidth

* default - 5.0
### ExpAvgLatency: "Average Latency Threshold (ms)" (input:double)

Average Latency Threshold (ms)

* default - 0.7
### IterationDuration: "Iteration Duration" (input:u32)

Iteration Duration

* default - 60
### CommandTagName: "Command Tag Name" (input:string)

Tag name for associated commands

* default - 
### StepCount: "Bandwidth Step Count" (input:u32)

Bandwidth Step Count

* default - 5
### OvershootBw: "Overshoot Bandwidth" (input:double)

Overshoot Bandwidth

* default - 5.0
## UsedIn
* ITU-T Y.1564 CBS and EBS Burst Test

* ITU-T Y.1564 Service Configuration Test

* ITU-T Y.1564 Service Performance Test

