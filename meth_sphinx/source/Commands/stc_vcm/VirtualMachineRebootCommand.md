# VirtualMachineRebootCommand

Reboot a virtual machine

<font size="2">File Reference: stc_vcm.xml</font>

<text>Properties</text>

### VirtualMachineRunning: "Virtual Machine Running" (output:bool)

Boolean showing if the virtual machine is running

* default - false
### BootTimeoutSeconds: "Virtual Machine Boot Timeout Seconds" (input:u16)

The virtual machine boot timeout in seconds

* default - 120
### BootCheckSeconds: "Virtual Machine Boot Check Seconds" (input:u16)

The virtual machine boot poll interval in seconds

* default - 5
### VirtualMachineId: "Virtual Machine Id" (input:string)

The virtual machine Id from the list virtual machines command

* default - 
