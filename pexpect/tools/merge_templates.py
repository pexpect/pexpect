#!/usr/bin/env python

# I use this to keep the sourceforge pages up to date with the
# latest documentation and I like to keep a copy of the distribution
# on the web site so that it will be compatible with
# The Vaults of Parnasus which requires a direct URL link to a
# tar ball distribution. I don't advertise the package this way.

import pexpect, pyed
import sys, os, re

# extract the version number from the pexpect.py source.
d = pyed.pyed()
d.read ("pexpect.py")
d.first('^__version__')
r = re.search("'([0-9]\.[0-9])'", d.cur_line)
version = r.group(1)

# Edit the index.html to update current VERSION.
d = pyed.pyed()
d.read ("doc/index.template.html")
for cl in d.match_lines('.*VERSION.*'):
    d.cur_line = d.cur_line.replace('VERSION', version)
d.write("doc/index.html") 
    
# Edit the setup.py to update current VERSION.
d = pyed.pyed()
d.read ("setup.py.template")
for cl in d.match_lines('.*VERSION.*'):
    d.cur_line = d.cur_line.replace('VERSION', version)
d.write("setup.py") 
os.chmod("setup.py", 0755)

