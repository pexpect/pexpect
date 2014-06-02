#!/usr/bin/env python

'''
I used to use this to keep the sourceforge pages up to date with the
latest documentation and I like to keep a copy of the distribution
on the web site so that it will be compatible with
The Vaults of Parnasus which requires a direct URL link to a
tar ball distribution. I don't advertise the package this way.

PEXPECT LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2012, Noah Spurrier <noah@noah.org>
    PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
    PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
    COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

'''

import pexpect
import getpass
import sys

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

