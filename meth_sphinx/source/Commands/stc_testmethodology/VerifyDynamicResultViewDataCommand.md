# VerifyDynamicResultViewDataCommand

Verify that DRV yields a result count that meets the specified limits.

<font size="2">File Reference: stc_testmethodology.xml</font>

<text>Properties</text>

### MaxResultCount: "Max Result Count (Inclusive)" (input:u64)

Maximum acceptable result count when OperationType is Between.

* default - 0
### MinResultCount: "Min Result Count (Inclusive)" (input:u64)

Minimum acceptable result count when OperationType is Between.

* default - 0
### DynamicResultViewName: "Dynamic Result View Name" (input:string)

Dynamic Result View Name.

* default - 
### ResultCount: "Result Count" (input:u64)

Result count to compare to DRV yield based on OperationType. Valid for all OperationType values except Between.

* default - 0
### OperationType: "Operation Type" (input:u8)

Comparision operator

* default - GREATER_THAN
