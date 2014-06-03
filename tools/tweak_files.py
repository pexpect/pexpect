'''

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

import pyed
import os
import re

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
