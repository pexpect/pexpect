Pexpect
a Pure Python "Expect like" module

To work with this CVS repository you should source the cvs.conf file.
    . ./cvs.conf

The purpose of the Pexpect module is to make Python be a better glue.

Pexpect works like Don Libes' Expect. Use Pexpect when you want to
control another application. It allows you to start a child
application and have your script control it as if a human were
typing commands.

Pexpect is a Python module for spawning child applications; 
controlling them; and responding to expected patterns in their 
output. Pexpect can be used for automating interactive applications
such as ssh, ftp, passwd, telnet, etc. It can be used to a automate
setup scripts for duplicating software package installations on
different servers. It can be used for automated software testing.
Pexpect is in the spirit of Don Libes' Expect, but Pexpect is pure
Python. Other Expect-like modules for Python require TCL and Expect
or require C extensions to be compiled. Pexpect does not use C,
Expect, or TCL extensions. It should work on any platform that
supports the standard Python pty module. The Pexpect interface was
designed to be easy to use so that simple tasks are easy.

License: Python Software Foundation License

Noah Spurrier
http://pexpect.sourceforge.net/


