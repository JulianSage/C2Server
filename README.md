# Villain
[![Python](https://img.shields.io/badge/python-%E2%89%A5%203.6-yellow.svg)](https://www.python.org/) 
<img src="https://img.shields.io/badge/powershell-%E2%89%A5%20v3.0-blue">
[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![License](https://img.shields.io/badge/license-BSD-red.svg)](https://github.com/t3l3machus/hoaxshell/blob/main/LICENSE.md)
<img src="https://img.shields.io/badge/Maintained%3F-Yes-96c40f">

## Purpose
Villain is a backdoor generator and reverse shell handler for Windows and Linux machines that supports multiple sessions. It also includes utilities that allow a user to connect with sibling servers (other machines running Villain) and share their backdoor shell sessions, handy for quickly connecting  with others working as a team and stuff like that. Additionally, this tool has a build in auto-obfuscate backdoor payload function to assist users in bypassing AV solutions (for Windows payloads).

**Disclaimer**: Running the payloads generated by this tool against hosts that you do not have explicit permission to test is illegal. You are responsible for any trouble you may cause by using this tool.

***This is an early release currectly being tested.***

An important part of this tool's functionality is inherited from [HoaxShell](https://github.com/t3l3machus/hoaxshell). One could say that, it is an evolved, steroids induced version of it.


## Approach
The reverse shell payloads generated by this tool abuse the http(s) protocol to establish a beacon-like reverse shell, based on the following concept:  

![image](https://user-images.githubusercontent.com/75489922/198854691-e749d0f2-0309-452c-ad37-c167814fb9db.png)


## Contributions
There are parts of this project that i removed before publishing because i considered them to be buggy or hard to maintain (at this early stage).
If you have an idea for an addition that comes with a significant chunk of code, I suggest you first contact me to discuss if there's something similar already in the making, before making a PR. 


