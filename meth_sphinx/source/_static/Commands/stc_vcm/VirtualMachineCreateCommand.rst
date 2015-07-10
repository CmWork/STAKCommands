# VirtualMachineCreateCommand

Create a virtual machine

<font size="2">File Reference: stc_vcm.xml</font>

## Properties

### ResourcePoolName: "Vsphere Resourcepool Name" (input:string)

The name specifying the desired Vsphere resourcepool

* default - 
### Count: "Virtual Machine Count" (input:u16)

The virtual machine count

* default - 1
### DatastoreName: "Vsphere Datastore Name" (input:string)

The name specifying the desired Vsphere datastore

* default - 
### SizeName: "Virtual Machine Size Name" (input:string)

The name of desired virtual machine size from the list sizes command

* default - 
### VirtualMachineId: "Virtual Machine Id" (output:string)

The virtual machine Id

* default - 
### Url: "Virtual Machine Url" (output:string)

The virtual machine Url

* default - 
### IpAddr: "Ip Address" (input:string)

The Ip address if the address mode is static

* default - 
### NtpServer: "Ntp Server" (input:string)

The Ntp server Ip address

* default - 
### HostName: "Vsphere Host Name" (input:string)

The name specifying the Vsphere host

* default - 
### AddrMode: "Address Mode" (input:string)

The address mode, either static or dhcp

* default - 
### Netmask: "Netmask" (input:string)

The netmask if the address mode is static.

* default - 
### BootCheckSeconds: "Virtual Machine Boot Check Seconds" (input:u16)

The virtual machine boot polling interval in seconds

* default - 5
### DatacenterName: "Vsphere Datacenter Name" (input:string)

The name specifying the Vsphere datacenter

* default - 
### LicenseServer: "License Server" (input:string)

The license server Ip address

* default - 
### BootTimeoutSeconds: "Virtual Machine Boot Timeout Seconds" (input:u16)

The virtual machine boot timeout in seconds

* default - 120
### ImageName: "Virtual Machine Image Name" (input:string)

The name of the desired virtual machine image from the list images command

* default - 
### PortSpeed: "Port Speed" (input:string)

The desired port speed either 1G or 10G

* default - 1G
### Gateway: "Gateway" (input:string)

The gateway if the address mode is static

* default - 
### VirtualMachineRunning: "Virtual Machine Running" (output:bool)

Boolean showing if the virtual machine is running

* default - false
### VirtualMachineName: "Virtual Machine Name" (input:string)

The desired virtual machine name

* default - 
### NetworkList: "Network List" (input:string)

The network list for this virtual machine from the list networks command

* default - 
