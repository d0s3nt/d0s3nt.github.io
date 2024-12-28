---
layout: post
title: "UnderPass"
date: 2024-12-28
categories: hackthebox
---


starting with nmap

```bash
# Nmap 7.94SVN scan initiated Sat Dec 21 20:11:10 2024 as: /usr/lib/nmap/nmap -sC -sV -p- -T4 -oN nmap 10.129.248.201
Warning: 10.129.248.201 giving up on port because retransmission cap hit (6).
Nmap scan report for 10.129.248.201 (10.129.248.201)
Host is up (0.090s latency).
Not shown: 65420 closed tcp ports (reset), 113 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 8.9p1 Ubuntu 3ubuntu0.10 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   256 48:b0:d2:c7:29:26:ae:3d:fb:b7:6b:0f:f5:4d:2a:ea (ECDSA)
|_  256 cb:61:64:b8:1b:1b:b5:ba:b8:45:86:c5:16:bb:e2:a2 (ED25519)
80/tcp open  http    Apache httpd 2.4.52 ((Ubuntu))
|_http-title: Apache2 Ubuntu Default Page: It works
|_http-server-header: Apache/2.4.52 (Ubuntu)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Sat Dec 21 20:26:56 2024 -- 1 IP address (1 host up) scanned in 945.64 seconds
➜  underpass git:(main) ✗
```


just an apache server , trying to fuzz but no result .

I was clueless so I ran another scan against UDP ports

```bash
sudo nmap -sU -T4 -oN nmap_udp 10.129.79.195 -Pn
```

![[Pasted image 20241221235520.png]]

let's enumerate SNMP 


```bash
snmpwalk -v2c -c public 10.129.79.195
```

![[Pasted image 20241221232505.png]]


so we got domain and `daloradius` which is a CMS

![[Pasted image 20241221232613.png]]


I used this https://github.com/lirantal/daloradius/blob/master/  , to enumerate website 

so I found some files like http://underpass.htb/daloradius/Dockerfile


![[Pasted image 20241221232838.png]]

I tried the default creds against http://underpass.htb/daloradius/app/users/login.php but useless .

after some search in GitHub , another login portal was discovered 
http://underpass.htb/daloradius/app/operators/login.php

login with default creds 


we can find a list of users 

![[Pasted image 20241221233105.png]]


![[Pasted image 20241221233128.png]]

[crackstation](https://crackstation.net/) to crack the hash 


`underwaterfriends`

![[Pasted image 20241221233256.png]]



### root



```bash
sudo -l
```

![[Pasted image 20241221233338.png]]

when we `mosh-server` we got KEY and port

![[Pasted image 20241221233419.png]]


using `mosh-client` we can get root

```bash
 MOSH_KEY=S1bavDXgiegwtNo04fZYVQ  mosh-client  127.0.0.1 60001
```


![[Pasted image 20241221233613.png]]