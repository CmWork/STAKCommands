# ScalingValidatePortsCommand

Calculate Resource Requirements Across Ports

<font size="2">File Reference: stc_testintel.xml</font>

<text>Properties</text>

### Profile: "Port/Feature Profile JSON String" (input:string)

Ports and features required. Must match ProfileSchema.

* default - {"portProfiles":[]}
### VerdictSchema: "Detailed Verdict Schema" (input:string)

Schema for DetailedVerdict

* default - {"$schema":"http://json-schema.org/schema#","type":"array","items":{"type":"object","properties":{"profileId":{"type":"string"},"portLocations":{"type":"array","items":{"type":"object","properties":{"location":{"type":"string"},"confidence":{"type":"number","minimum":0,"maximum":100},"reason":{"type":"string"}}}},"portTypes":{"type":"array","items":{"type":"object","properties":{"portType":{"type":"string"},"confidence":{"type":"number","minimum":0,"maximum":100},"reason":{"type":"string"}}}}}}}
### Verdict: "Per port results in JSON" (output:string)

Per port results in JSON

* default - []
### ProfileSchema: "Port/Feature Profile JSON Schema" (input:string)

Schema for Profile

* default - {"$schema":"http://json-schema.org/schema#","type":"object","properties":{"portProfiles":{"type":"array","items":{"type":"object","properties":{"profileId":{"type":"string"},"portLocations":{"type":"array","items":{"type":"string"}},"portCount":{"type":"number"}},"required":["profileId"]}}},"required":["portProfiles"]}
