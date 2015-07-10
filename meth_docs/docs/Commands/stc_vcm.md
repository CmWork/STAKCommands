# ListVersionsCommand

Retrieve the API and product versions

<h2>- Properties</h2>

<h3>StatusList: "Version Status List" (output:string)</h3>

The list of version descriptions

* default - 

<h3>ProductVersion: "Virtual Chassis Manager Version" (output:string)</h3>

The Virtual Chassis Manager product version

* default - 

<h3>VersionList: "Version List" (output:string)</h3>

The list of version values

* default - 

# VirtualMachineDestroyCommand

Destroy a virtual machine

<h2>- Properties</h2>

<h3>VirtualMachinePresent: "Virtual Machine Present" (output:bool)</h3>

Boolean showing if the virtual machine is present

* default - true

<h3>VirtualMachineId: "Virtual Machine Id" (input:string)</h3>

The virtual machine Id to destroy from the list virtual machines command

* default - 

# ListLogsCommand

List the available log files

<h2>- Properties</h2>

<h3>UrlList: "Log Url List" (output:string)</h3>

The list of log urls

* default - 

<h3>LogSizeList: "Log Size List" (output:string)</h3>

The list of log sizes

* default - 

<h3>LogNameList: "Log Name List" (output:string)</h3>

The list of log file names used in the get logs command

* default - 

# VirtualMachineRebootCommand

Reboot a virtual machine

<h2>- Properties</h2>

<h3>VirtualMachineRunning: "Virtual Machine Running" (output:bool)</h3>

Boolean showing if the virtual machine is running

* default - false

<h3>BootTimeoutSeconds: "Virtual Machine Boot Timeout Seconds" (input:u16)</h3>

The virtual machine boot timeout in seconds

* default - 120

<h3>BootCheckSeconds: "Virtual Machine Boot Check Seconds" (input:u16)</h3>

The virtual machine boot poll interval in seconds

* default - 5

<h3>VirtualMachineId: "Virtual Machine Id" (input:string)</h3>

The virtual machine Id from the list virtual machines command

* default - 

# VirtualMachineCreateCommand

Create a virtual machine

<h2>- Properties</h2>

<h3>ResourcePoolName: "Vsphere Resourcepool Name" (input:string)</h3>

The name specifying the desired Vsphere resourcepool

* default - 

<h3>Count: "Virtual Machine Count" (input:u16)</h3>

The virtual machine count

* default - 1

<h3>DatastoreName: "Vsphere Datastore Name" (input:string)</h3>

The name specifying the desired Vsphere datastore

* default - 

<h3>SizeName: "Virtual Machine Size Name" (input:string)</h3>

The name of desired virtual machine size from the list sizes command

* default - 

<h3>VirtualMachineId: "Virtual Machine Id" (output:string)</h3>

The virtual machine Id

* default - 

<h3>Url: "Virtual Machine Url" (output:string)</h3>

The virtual machine Url

* default - 

<h3>IpAddr: "Ip Address" (input:string)</h3>

The Ip address if the address mode is static

* default - 

<h3>NtpServer: "Ntp Server" (input:string)</h3>

The Ntp server Ip address

* default - 

<h3>HostName: "Vsphere Host Name" (input:string)</h3>

The name specifying the Vsphere host

* default - 

<h3>AddrMode: "Address Mode" (input:string)</h3>

The address mode, either static or dhcp

* default - 

<h3>Netmask: "Netmask" (input:string)</h3>

The netmask if the address mode is static.

* default - 

<h3>BootCheckSeconds: "Virtual Machine Boot Check Seconds" (input:u16)</h3>

The virtual machine boot polling interval in seconds

* default - 5

<h3>DatacenterName: "Vsphere Datacenter Name" (input:string)</h3>

The name specifying the Vsphere datacenter

* default - 

<h3>LicenseServer: "License Server" (input:string)</h3>

The license server Ip address

* default - 

<h3>BootTimeoutSeconds: "Virtual Machine Boot Timeout Seconds" (input:u16)</h3>

The virtual machine boot timeout in seconds

* default - 120

<h3>ImageName: "Virtual Machine Image Name" (input:string)</h3>

The name of the desired virtual machine image from the list images command

* default - 

<h3>PortSpeed: "Port Speed" (input:string)</h3>

The desired port speed either 1G or 10G

* default - 1G

<h3>Gateway: "Gateway" (input:string)</h3>

The gateway if the address mode is static

* default - 

<h3>VirtualMachineRunning: "Virtual Machine Running" (output:bool)</h3>

Boolean showing if the virtual machine is running

* default - false

<h3>VirtualMachineName: "Virtual Machine Name" (input:string)</h3>

The desired virtual machine name

* default - 

<h3>NetworkList: "Network List" (input:string)</h3>

The network list for this virtual machine from the list networks command

* default - 

# BaseCommand

Virtual Chassis Manager Base Command

<h2>- Properties</h2>

<h3>Port: "Port" (input:u16)</h3>

The virtual chassis manager TCP port number

* default - 8080

<h3>Server: "Server" (input:string)</h3>

The virtual chassis manager server IP or DNS name

* default - 

# ListNetworksCommand

List the available networks

<h2>- Properties</h2>

<h3>NetworkNameList: "Network Name List" (output:string)</h3>

The available network names used in the create command

* default - 

<h3>NetworkIdList: "Network Id List" (output:string)</h3>

The available network Ids

* default - 

# ListImagesCommand

List the available VM images

<h2>- Properties</h2>

<h3>ImageIdList: "Image Id List" (output:string)</h3>

The available image Ids

* default - 

<h3>ImageNameList: "Image Name List" (output:string)</h3>

The available image names used in the create command

* default - 

# GetLogCommand

Retrieve a log file

<h2>- Properties</h2>

<h3>SavePath: "Saved Log Path" (input:outputFilePath)</h3>

Where to save the log file

* default - 

<h3>LogFileName: "Log File To Save" (input:string)</h3>

The log file to retrieve

* default - 

# ListSizesCommand

List the available sizes

<h2>- Properties</h2>

<h3>VcpusList: "VCPUs List" (output:string)</h3>

The virtual CPUs configured for this size

* default - 

<h3>DiskList: "Disk List" (output:string)</h3>

The disk configured for this size

* default - 

<h3>SizeNameList: "Size Name List" (output:string)</h3>

The available size names used in the create command

* default - 

<h3>SizeIdList: "Size Id List" (output:string)</h3>

The available size Ids

* default - 

<h3>RamList: "RAM List" (output:string)</h3>

The RAM configured for this size

* default - 

# VirtualMachineInfoCommand

Retrieve virtual machine configuration information

<h2>- Properties</h2>

<h3>AddrList: "IP Address List" (output:string)</h3>

The IP Addresses for each network on this virtual machine

* default - 

<h3>VirtualMachineFound: "Virtual Machine Found" (output:bool)</h3>

Boolean showing if the virtual machine was found

* default - false

<h3>NetworkList: "Network List" (output:string)</h3>

The networks configured on this virtual machine

* default - 

<h3>VirtualMachineId: "Virtual Machine Id" (input:string)</h3>

The virtual machine Id from the list virtual machines command

* default - 

# ListVirtualMachinesCommand

List the virtual machines

<h2>- Properties</h2>

<h3>VmIdList: "VM Id List" (output:string)</h3>

The virtual machine Ids used in the info and reboot commands, returned from the create command

* default - 

<h3>VmNameList: "VM Name List" (output:string)</h3>

The virtual machine names specified in the create command

* default - 

# CredentialsCommand

<font color="red">MISSING DESCRIPTION</font>

<h2>- Properties</h2>

<h3>ProviderServer: "Provider Server" (input:string)</h3>

The server Ip or name to connect to for your virtual environment

* default - localhost

<h3>ProviderPassword: "Provider Password" (input:string)</h3>

The password to supply to your virtual environment

* default - password

<h3>ProviderUser: "Provider User" (input:string)</h3>

The user name to supply to your virtual environment

* default - root

<h3>ProviderTenant: "Provider Tenant" (input:string)</h3>

The OpenStack tenant or resource group

* default - demo

<h3>Provider: "Technology Provider" (input:string)</h3>

The supporting technology or vendor that implements your virtual environment

* default - Simulator

