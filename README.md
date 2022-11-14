# Villain
[![Python](https://img.shields.io/badge/Python-%E2%89%A5%203.6-yellow.svg)](https://www.python.org/) 
<img src="https://img.shields.io/badge/PowerShell-%E2%89%A5%20v3.0-blue">
<img src="https://img.shields.io/badge/Developed%20on-kali%20linux-blueviolet">
[![License](https://img.shields.io/badge/License-CC%20Attr--NonCommercial%204.0-red)](https://github.com/t3l3machus/Villain/blob/main/LICENSE.md)
<img src="https://img.shields.io/badge/Maintained%3F-Yes-96c40f">

## Purpose
Villain is a Windows & Linux backdoor generator and multi-session handler that allows users to connect with sibling servers (other machines running Villain) and share their backdoor sessions, handy for working as a team.  

The main idea behind the payloads generated by this tool is inherited from [HoaxShell](https://github.com/t3l3machus/hoaxshell). One could say that Villain is an evolved, steroid-induced version of it.

:zap: **This is an early release currently being tested.**

### Video Presentation
https://www.youtube.com/watch?v=NqZEmBsLCvQ

**Disclaimer**: Running the payloads generated by this tool against hosts that you do not have explicit permission to test is illegal. You are responsible for any trouble you may cause by using this tool.

## Preview
![image](https://user-images.githubusercontent.com/75489922/201544082-e1233421-f319-47b5-9e5e-d95647026dc0.png)

## Installation & Usage
```
git clone https://github.com/t3l3machus/Villain
cd ./Villain
pip3 install -r requirements.txt
```
You should run as root:
```
Villain.py [-h] [-p PORT] [-x HOAX_PORT] [-c CERTFILE] [-k KEYFILE] [-u] [-q]
```
For more information about using Villain check out the [Usage Guide](https://github.com/t3l3machus/Villain/edit/main/README.md).

## Important Notes
1. Villain has a built-in auto-obfuscate payload function to assist users in bypassing AV solutions (for Windows payloads). As a result, payloads are undetected (for the time being).
2. Each generated payload is going to work only once. An already used payload cannot be reused to establish a session.
3. The communication between sibling servers is AES encrypted using the recipient sibling server's ID as the encryption KEY and the 16 first bytes of the local server's ID as IV. During the initial connection handshake of two sibling servers, each server's ID is exchanged clear text, meaning that the handshake could be captured and used to decrypt traffic between sibling servers. I know it's "weak" that way. It's not supposed to be super secure as this tool was designed to be used during penetration testing / red team assessments, for which this encryption schema should be enough.
4. Villain instances connected with each other (sibling servers) must be able to directly reach each other as well. I intend to add a network route mapping utility so that sibling servers can use one another as a proxy to achieve cross network communication between them.

## Approach
A few notes about the http(s) beacon-like reverse shell approach:
![image](https://user-images.githubusercontent.com/75489922/201542083-68280123-6ea0-4653-b129-3124ad9bb041.png)

### Limitations
 - A backdoor shell is going to hang if you execute a command that initiates an interactive session. For more information [read this](https://github.com/t3l3machus/hoaxshell#Limitations).
### Advantages
 - When it comes to Windows, the generated payloads can run even in PowerShell constraint Language Mode.
 - The generated payloads can run even by users with limited privileges.

## Contributions
Pull requests are generally welcome. Please, keep in mind: I am constantly working on new offsec tools as well as maintaining several existing ones. I rarely accept pull requests because I either have a plan for the course of a project or I evaluate that it would be hard to test and/or maintain the foreign code. It doesn't have to do with how good or bad is an idea, it's just too much work and also, I am kind of developing all these tools to learn myself.

There are parts of this project that were removed before publishing because I considered them to be buggy or hard to maintain (at this early stage).
If you have an idea for an addition that comes with a significant chunk of code, I suggest you first contact me to discuss if there's something similar already in the making, before making a PR. 
