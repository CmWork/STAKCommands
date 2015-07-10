# ScalingGetValidPortTypesCommand

Get Port Types Meeting Resource Requirements

<font size="2">File Reference: stc_testintel.xml</font>

## Properties

### MinCores: "Minimum number of cores required" (input:u32)

Minimum number of cores required

* default - 1
### FilterPortTypeList: "Filter Port Type List" (input:string)

Filter output port type list by limiting to valid ports in this list

* default - 
### PortTypeList: "Port Types" (output:string)

Port type (a.k.a. test module part number) list

* default - 
### MinSpiMips: "Minimum amount of SpiMIPS required" (input:u32)

Minimum amount of processing power required in SpiMIPS

* default - 100
### MinMemoryMb: "Minimum memory in MB" (input:u32)

Minimum port memory required in MB

* default - 512
