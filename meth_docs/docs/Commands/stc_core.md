# ReleaseObjectReferenceCommand

<font color="red">MISSING DESCRIPTION</font>

<h2>- Properties</h2>

<h3>Key: "Key to remove from Persistent Storage (empty to remove everything)" (input:string)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - 

# GetChassisInfoCommand

<font color="red">MISSING DESCRIPTION</font>

<h2>- Properties</h2>

<h3>AddrList: "Chassis IP/Hostname" (input:string)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - 

<h3>AutoConnect: "Auto Connect" (input:bool)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - false

<h3>ChassisInfoList: "Chassis Info" (output:string)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - 

# DownloadFeatureLicenseCommand

<font color="red">MISSING DESCRIPTION</font>

<h2>- Properties</h2>

<h3>TargetFilename: "Target Filename" (input:outputFilePath)</h3>

Download location of the feature license

* default - Features.lic

<h3>Server: "License Server" (input:string)</h3>

The license server IP or DNS name

* default - 

# GetSupportedSpeedsCommand

<font color="red">MISSING DESCRIPTION</font>

<h2>- Properties</h2>

<h3>SpeedInfoList: "Speed Info" (output:string)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - 

<h3>PhyTestModule: "Physical Test Module" (input:handle)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - 0

<h3>PhyType: "Physical Port Type" (input:u32)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - LAN

# EnableUserLogsCommand

<font color="red">MISSING DESCRIPTION</font>

<h2>- Properties</h2>

<h3>Enable: "Enable" (input:bool)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - true

<h3>Limit: "Limit" (input:u32)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - 5000

# GetUserErrorLogsCommand

<font color="red">MISSING DESCRIPTION</font>

<h2>- Properties</h2>

<h3>Clear: "Clear" (input:bool)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - true

<h3>IncludeWarnings: "Include Warnings" (input:bool)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - false

<h3>LogList: "Log List" (output:string)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - 

# ArchiveDiagnosticLogsCommand

<font color="red">MISSING DESCRIPTION</font>

<h2>- Properties</h2>

<h3>FileName: "File Name" (input:outputFilePath)</h3>

<font color="red">MISSING DESCRIPTION</font>

* default - diagnostics.tgz

# CreateAndReserveVirtualPortsCommand

Create STCv ports in QManager and create and reserve associated STC Ports

<h2>- Properties</h2>

<h3>VmImage: "VM Image" (input:string)</h3>

Name of image file or build number.  If empty, then use the latest build on the qmanager server.  If parameter starts with '#' for example #4.50.0273, then use the STCv image for that build.

* default - 

<h3>PortLocations: "Virtual Port Locations" (output:string)</h3>

List of locations of virtual ports

* default - 

<h3>Description: "VM Description" (input:string)</h3>

Text to describe of VM instances

* default - STCv created by STAK command

<h3>PortCount: "Port Count" (input:s32)</h3>

Number of virtual port instances to create

* default - 2

<h3>VmMem: "VM Memory" (input:s32)</h3>

MB of memory to allocate to each VM instance.  If zero, use qmanager default for STCv.

* default - 512

<h3>VmList: "Virtual Machine IDs" (output:string)</h3>

List of VM ID values for virtual ports

* default - 

<h3>User: "VM User" (input:string)</h3>

Name of user creating virtual ports.

* default - anonymous

<h3>TtlMinutes: "Minutes to Live" (input:s32)</h3>

Minutes before the VM is automatically stopped.  If empty, then use qmanager default.

* default - 120

<h3>QmServer: "QManager Server URL" (input:string)</h3>

URL of QManager server to use for managing VM instances

* default - http://qmanager.cal.ci.spirentcom.com:8080

<h3>Cores: "VM CPUs" (input:u32)</h3>

Logical CPUs for each VM.  If zero, use qmanager default for STCv.

* default - 1

<h3>LicenseServer: "License Server" (input:string)</h3>

License server address.  If empty, use qmanager default.

* default - 

<h3>Ports: "Virtual Port Handles" (output:handle)</h3>

List of handles for virtual ports

* default - 

<h3>UseSocket: "Connect VMs using socket" (input:bool)</h3>

If True, connect VM instances with socket.  If False or empty then connect VM instances using vbridge.  Only set to True if needed for specific types of traffic.

* default - false

# DetachAndStopVirtualPortsCommand

Detach STC Ports from the test session and stop the associated STCv ports in QManager

<h2>- Properties</h2>

<h3>User: "VM User" (input:string)</h3>

Name of user who created the virtual ports.

* default - anonymous

<h3>QmServer: "QManager Server URL" (input:string)</h3>

URL of QManager server to use for managing VM instances

* default - http://qmanager.cal.ci.spirentcom.com:8080

