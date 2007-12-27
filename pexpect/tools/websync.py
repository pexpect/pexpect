#!/usr/bin/env python

# I use this to keep the sourceforge pages up to date with the
# latest documentation and I like to keep a copy of the distribution
# on the web site so that it will be compatible with
# The Vaults of Parnasus which requires a direct URL link to a
# tar ball distribution. I don't advertise the package this way.

import pexpect, pyed
import getpass
import sys, os

X = getpass.getpass('Password: ')
pp_pattern=["(?i)password:", "(?i)enter passphrase for key '.*?':"]

p = pexpect.spawn ('scp -r doc/. noah@shell.sourceforge.net:/home/groups/p/pe/pexpect/htdocs/.')
p.logfile_read = sys.stdout
p.expect (pp_pattern)
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

p = pexpect.spawn ('scp doc/clean.css doc/email.png noah@shell.sourceforge.net:/home/groups/p/pe/pexpect/htdocs/clean.css')
p.logfile_read = sys.stdout
p.expect (pp_pattern)
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

#p = pexpect.spawn ('ssh noah@use-pr-shell1.sourceforge.net "cd htdocs;tar zxvf pexpect-doc.tgz"')
#p.logfile_read = sys.stdout
#p.expect ('password:')
#p.sendline (X)
#p.expect (pexpect.EOF)
#print p.before

p = pexpect.spawn ('scp dist/pexpect-*.tar.gz noah@shell.sourceforge.net:/home/groups/p/pe/pexpect/htdocs/.')
p.logfile_read = sys.stdout
p.expect (pp_pattern)
p.sendline (X)
p.expect (pexpect.EOF)
print p.before

