import pyed
import re

# extract the version number from the pexpect.py source.
doc = file ('../pexpect.py','rb').read()
d = pyed.pyed(doc)
d.first('^__version__')
r = re.search("'([0-9]\.[0-9])'", d.cur_line)
version = r.group(1)

