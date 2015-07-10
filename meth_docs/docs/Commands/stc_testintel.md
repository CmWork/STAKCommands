# ScalingGetValidPortTypesCommand

Get Port Types Meeting Resource Requirements

<h2>- Properties</h2>

<h3>MinCores: "Minimum number of cores required" (input:u32)</h3>

Minimum number of cores required

* default - 1

<h3>FilterPortTypeList: "Filter Port Type List" (input:string)</h3>

Filter output port type list by limiting to valid ports in this list

* default - 

<h3>PortTypeList: "Port Types" (output:string)</h3>

Port type (a.k.a. test module part number) list

* default - 

<h3>MinSpiMips: "Minimum amount of SpiMIPS required" (input:u32)</h3>

Minimum amount of processing power required in SpiMIPS

* default - 100

<h3>MinMemoryMb: "Minimum memory in MB" (input:u32)</h3>

Minimum port memory required in MB

* default - 512

# TrafficSummarizeCommand

<font color="red">MISSING DESCRIPTION</font>

<h2>- Properties</h2>

<h3>NameList: "Names" (output:string)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - 

<h3>ValueList: "Values" (output:double)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - 0

<h3>QueryPort: "Query the Port for Additional Information" (input:bool)</h3>

Retrieve additional information (e.g. memory usage) from the port.

* default - false

<h3>LogFileName: "Log File Name" (input:string)</h3>

File name to log output. Empty string means don't log.

* default - 

<h3>SoftStreamsOnly: "Soft Streams Only" (input:bool)</h3>

Limit summary to soft streams.

* default - true

<h3>Port: "Port" (input:handle)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - 0

# UsageCheckCommand

Check Resource Usage

<h2>- Properties</h2>

<h3>TestPoint: "Test Point" (input:string)</h3>

Unique string for this test and this point in the test

* default - 

# ScalingValidatePortsCommand

Calculate Resource Requirements Across Ports

<h2>- Properties</h2>

<h3>Profile: "Port/Feature Profile JSON String" (input:string)</h3>

Ports and features required. Must match ProfileSchema.

* default - {"portProfiles":[]}

<h3>VerdictSchema: "Detailed Verdict Schema" (input:string)</h3>

Schema for DetailedVerdict

* default - {"$schema":"http://json-schema.org/schema#","type":"array","items":{"type":"object","properties":{"profileId":{"type":"string"},"portLocations":{"type":"array","items":{"type":"object","properties":{"location":{"type":"string"},"confidence":{"type":"number","minimum":0,"maximum":100},"reason":{"type":"string"}}}},"portTypes":{"type":"array","items":{"type":"object","properties":{"portType":{"type":"string"},"confidence":{"type":"number","minimum":0,"maximum":100},"reason":{"type":"string"}}}}}}}

<h3>Verdict: "Per port results in JSON" (output:string)</h3>

Per port results in JSON

* default - []

<h3>ProfileSchema: "Port/Feature Profile JSON Schema" (input:string)</h3>

Schema for Profile

* default - {"$schema":"http://json-schema.org/schema#","type":"object","properties":{"portProfiles":{"type":"array","items":{"type":"object","properties":{"profileId":{"type":"string"},"portLocations":{"type":"array","items":{"type":"string"}},"portCount":{"type":"number"}},"required":["profileId"]}}},"required":["portProfiles"]}

# ScalingCheckResourcesCommand

Calculate Resource Requirements

<h2>- Properties</h2>

<h3>MinCores: "Minimum number of cores required" (output:u32)</h3>

Minimum number of cores required

* default - 

<h3>MinSpiMips: "Minimum amount of SpiMIPS required" (output:u32)</h3>

Minimum amount of processing power required in SpiMIPS

* default - 

<h3>FeatureNameList: "List of Feature Names" (input:string)</h3>

Features required. Length must match FeatureValueList.

* default - 

<h3>FeatureValueList: "List of Feature Values" (input:string)</h3>

Values for required features. Length must match FeatureNameList

* default - 

<h3>MinMemoryMb: "Minimum memory in MB" (output:u32)</h3>

Minimum port memory required in MB

* default - 

