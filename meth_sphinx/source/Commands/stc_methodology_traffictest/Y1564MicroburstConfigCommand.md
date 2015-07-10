# Y1564MicroburstConfigCommand

Configure Y.1564 Microburst Test

<font size="2">File Reference: stc_methodology_traffictest.xml</font>

<text>Properties</text>

### MicroburstRateUnit: "Microburst Rate Unit" (input:u8)

Microburst Rate Unit

* default - PERCENT_LINE_RATE
### LeftTagName: "Left Port Group Tag Name" (input:string)

Left Port Group Tag Name

* default - 
### MicroburstTagName: "Tag Name for Microburst Streams" (input:string)

Tag Name for Microburst Streams

* default - ttMicroburst
### FrameSize: "Frame Size (bytes)" (input:u16)

Frame Size (bytes)

* default - 128
### RightTagName: "Right Port Group Tag Name" (input:string)

Right Port Group Tag Name

* default - 
### MicroburstMaxRate: "Microburst Maximum Rate" (input:double)

Microburst Maximum Rate

* default - 100.0
### DeltaWidth: "Delta Width" (input:u32)

Delta Width in Packets

* default - 500
### MaxDeltaCount: "Maximum Delta Count per Burst" (input:u32)

Maximum Delta Count per Burst

* default - 10
### RandomSeedValue: "Random Seed Value" (input:u32)

Random Seed Value

* default - 0
### NominalRateUnit: "Nominal Rate Unit" (input:u8)

Nominal Rate Unit

* default - PERCENT_LINE_RATE
### EnableLearning: "Enable L2/L3 Learning" (input:bool)

Enable L2/L3 Learning

* default - false
### MixTagName: "Mix Container Tag Name" (input:string)

Mix Container Tag Name

* default - 
### BestEffortTagName: "Tag Name for Best Effort Streams" (input:string)

Tag Name for Best Effort Streams

* default - ttBeStream
### MaxUniqueAddrCount: "Maximum Unique Address Count" (input:u32)

Max Unique Address Count

* default - 500
### NominalRate: "Nominal Rates" (input:double)

Nominal Rate

* default - 10.0
### EnableRandomSeed: "Enable Random Seed" (input:bool)

Enable Random Seed

* default - false
### MaxImg: "Maximum Inter-Microburst Gap (frames)" (input:u32)

Maximum Inter-Microburst Gap (frames)

* default - 500
### MicroburstFileName: "Microburst Configuration File" (input:inputFilePath)

Microburst Configuration File

* default - 
## UsedIn
* ITU-T Y.1564 Microburst Test

