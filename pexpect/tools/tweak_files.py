import pyed
import re

# extract the version number from the pexpect.py source.
d = pyed.pyed()
d.read ("../pexpect.py")
d.first('^__version__')
r = re.search("'([0-9]\.[0-9])'", d.cur_line)
version = r.group(1)

d = pyed.pyed()
d.read ("../doc/index.html")
for cl in d.match_lines('.*VERSION.*'):
    d.cur_line = d.cur_line.replace('VERSION', version)
d.write("../doc/index.html") 
    
