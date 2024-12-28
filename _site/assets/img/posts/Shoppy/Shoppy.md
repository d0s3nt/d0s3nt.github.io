
starting with nmap 
` sudo nmap -sC  -sV 10.10.11.180  -T4 -oN nmap_shoppy -p-   
![[Pasted image 20240621033417.png]]
port 80,9093

no idea what's the port 9093 is , so I will enumerate the web page first , the first page doesn't really show anything except I useless counter
![[Pasted image 20240621033546.png]]

`ffuf -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -u http://shoppy.htb/FUZZ -ic `
![[Pasted image 20240621033607.png]]

the login page does a really weird behavior when I inject `'` in the username parameter I got a timeout 