# CreateAndReserveVirtualPortsCommand

Create STCv ports in QManager and create and reserve associated STC Ports

<font size="2">File Reference: stc_core.xml</font>

<text>Properties</text>

### VmImage: "VM Image" (input:string)

Name of image file or build number.  If empty, then use the latest build on the qmanager server.  If parameter starts with '#' for example #4.50.0273, then use the STCv image for that build.

* default - 
### PortLocations: "Virtual Port Locations" (output:string)

List of locations of virtual ports

* default - 
### Description: "VM Description" (input:string)

Text to describe of VM instances

* default - STCv created by STAK command
### PortCount: "Port Count" (input:s32)

Number of virtual port instances to create

* default - 2
### VmMem: "VM Memory" (input:s32)

MB of memory to allocate to each VM instance.  If zero, use qmanager default for STCv.

* default - 512
### VmList: "Virtual Machine IDs" (output:string)

List of VM ID values for virtual ports

* default - 
### User: "VM User" (input:string)

Name of user creating virtual ports.

* default - anonymous
### TtlMinutes: "Minutes to Live" (input:s32)

Minutes before the VM is automatically stopped.  If empty, then use qmanager default.

* default - 120
### QmServer: "QManager Server URL" (input:string)

URL of QManager server to use for managing VM instances

* default - http://qmanager.cal.ci.spirentcom.com:8080
### Cores: "VM CPUs" (input:u32)

Logical CPUs for each VM.  If zero, use qmanager default for STCv.

* default - 1
### LicenseServer: "License Server" (input:string)

License server address.  If empty, use qmanager default.

* default - 
### Ports: "Virtual Port Handles" (output:handle)

List of handles for virtual ports

* default - 
### UseSocket: "Connect VMs using socket" (input:bool)

If True, connect VM instances with socket.  If False or empty then connect VM instances using vbridge.  Only set to True if needed for specific types of traffic.

* default - false
