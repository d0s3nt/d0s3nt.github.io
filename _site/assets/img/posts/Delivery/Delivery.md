
starting with nmap 
`sudo nmap -sC -sV -p- -T4 -oN delivery 10.10.10.222
`
![[Pasted image 20240525132457.png]]

two ports 80,8065 seems like two websites are hosted here 

we found  a new subdomain ![[Pasted image 20240525132613.png]]

seems like OsTicket

let's try to open a ticket 
![[Pasted image 20240525132720.png]]


![[Pasted image 20240525132827.png]]

let's view our ticket  5823990@delivery.htb

![[Pasted image 20240525132913.png]]![[Pasted image 20240525132929.png]]

at this point a tried an SSRF , https://www.exploit-db.com/exploits/49441
but didn't work , let's check the other website 

we can create account  

![[Pasted image 20240525133112.png]]

we need to verify our mail 
![[Pasted image 20240525133202.png]]

but the htb boxes are not connected to the internet so how tf we will get an email 


going back the OSTICKET , maybe we can use this to verify our mail since we have access to the thread of this ticket
![[Pasted image 20240525132827.png]]



we got this 
![[Pasted image 20240525133433.png]]


once we logged in , we found creds
![[Pasted image 20240525133531.png]]


now we can ssh into the box , and use Pwnkit to get root
![[Pasted image 20240525133605.png]]


that's what I did , but ippsec did another thing 

![[Pasted image 20240525152121.png]]

he use hashcat rule (best64), to create a wordlist of the ==PleasrSubscibe!==

and use tool like ==sucrack== https://github.com/hemp3l/sucrack

or  if we check the config file of the mattermost in the /opt , we could find credential of mysql
then get the root hash and crack it offline with hashcat and the wordlist we create before 