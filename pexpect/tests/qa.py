#!/usr/bin/env python
import commands
import signal

signal.signal(signal.SIGCHLD, signal.SIG_IGN)
print commands.getoutput('/bin/ls -l')

