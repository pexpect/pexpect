import pyed
import sys, os, re

# extract the version number from the pexpect.py source.
d = pyed.pyed()
d.read ("pexpect.py")
d.first('^__version__')
r = re.search("'([0-9]\.[0-9])'", d.cur_line)
version = r.group(1)

# Edit the index.html to update current VERSION.
d = pyed.pyed()
d.read ("doc/index.html.template")
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
