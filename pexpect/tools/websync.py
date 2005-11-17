#!/usr/bin/env python

# I use this to keep the sourceforge pages up to date with the
# latest documentation and I like to keep a copy of the distribution
# on the web site so that it will be compatible with
# The Vaults of Parnasus which requires a direct URL link to a
# tar ball distribution. I don't advertise the package this way.

import pexpect
import getpass
import sys, os

X = getpass.getpass('Password: ')

p = pexpect.spawn ('scp -r doc/. noah@use-pr-shell1.sourceforge.net:htdocs/.')
p.logfile = sys.stdout
p.expect ('password:')
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

p = pexpect.spawn ('scp doc/clean.css noah@use-pr-shell1.sourceforge.net:htdocs/clean.css')
p.logfile = sys.stdout
p.expect ('password:')
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

p = pexpect.spawn ('scp pexpect-doc.tgz noah@use-pr-shell1.sourceforge.net:htdocs/pexpect-doc.tgz')
p.logfile = sys.stdout
p.expect ('password:')
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

p = pexpect.spawn ('ssh noah@use-pr-shell1.sourceforge.net "cd htdocs;tar zxvf pexpect-doc.tgz"')
p.logfile = sys.stdout
p.expect ('password:')
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

p = pexpect.spawn ('scp pexpect-current.tgz noah@use-pr-shell1.sourceforge.net:htdocs/pexpect-current.tgz')
p.logfile = sys.stdout
p.expect ('password:')
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

