#!/usr/bin/env python

# I use this to keep the sourceforge pages up to date with the
# latest documentation and I like to keep a copy of the distribution
# on the web site so that it will be compatible with
# The Vaults of Parnasus which requires a direct URL link to a
# tar ball distribution. I don't advertise the package this way.

import pexpect
import getpass

X = getpass.getpass('Password: ')

p = pexpect.spawn ('ssh noah@use-pr-shell1.sourceforge.net "cd htdocs;rm -f index.html;wget http://www.noah.org/python/pexpect/index.html"')
p.expect ('password:')
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

p = pexpect.spawn ('ssh noah@use-pr-shell1.sourceforge.net "cd htdocs;rm -f clean.css;wget http://www.noah.org/python/pexpect/clean.css"')
p.expect ('password:')
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

p = pexpect.spawn ('scp pexpect-doc.tgz noah@use-pr-shell1.sourceforge.net:htdocs/pexpect-doc.tgz')
p.expect ('password:')
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

p = pexpect.spawn ('ssh noah@use-pr-shell1.sourceforge.net "cd htdocs;tar zxvf pexpect-doc.tgz"')
p.expect ('password:')
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

p = pexpect.spawn ('scp pexpect-current.tgz noah@use-pr-shell1.sourceforge.net:htdocs/pexpect-current.tgz')
p.expect ('password:')
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

