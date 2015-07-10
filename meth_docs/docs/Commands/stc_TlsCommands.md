# TlsKeyCertificateDeleteCommand

 A command to delete specified key/certificate file(s).

<h2>- Properties</h2>

<h3>FileNameList: "File Name List" (input:string)</h3>

Remote file(s) to delete.

* default - 

# TlsKeyCertificateEnumerateCommand

 A command to retrieve Private, Public, Certificate Files Available on a specific Port.

<h2>- Properties</h2>

<h3>PrivateKeyFiles: "Private Key List" (output:string)</h3>

List of private key files.

* default - 

<h3>CaCertificateFiles: "CA Certificate List" (output:string)</h3>

List of CA certificate files.

* default - 

<h3>CertificateFiles: "Certificate List" (output:string)</h3>

List of certificate files.

* default - 

# TlsKeyCertificateUploadCommand

A command to upload specified key/certificate file(s).

<h2>- Properties</h2>

<h3>FailurePortList: "Failure Port List" (output:handle)</h3>

List of ports on which upload failed.

* default - 0

<h3>FileNameList: "File Name List" (input:inputFilePath)</h3>

Local file(s) to upload.

* default - 

