#!/usr/bin/env python
"""This displays uptime information using uptime.
A bit redundant perhaps, but it demonstrates expecting for a
regular expression that uses subgroups.
"""

import pexpect
import re

# Different styles of uptime results.
#
# [x86] Linux 2.4 (Redhat 7.3)
#  2:06pm  up 63 days, 18 min,  3 users,  load average: 0.32, 0.08, 0.02
# [x86] Linux 2.4.18-14 (Redhat 8.0)
#  3:07pm  up 29 min,  1 user,  load average: 2.44, 2.51, 1.57
# [PPC - G4] MacOS X 10.1 SERVER Edition
# 2:11PM  up 3 days, 13:50, 3 users, load averages: 0.01, 0.00, 0.00
# [Sparc - R220] Sun Solaris (8)
#  2:13pm  up 22 min(s),  1 user,  load average: 0.02, 0.01, 0.01
# [x86] Linux 2.4.18-14 (Redhat 8)
# 11:36pm  up 4 days, 17:58,  1 user,  load average: 0.03, 0.01, 0.00

p = pexpect.spawn ('uptime')
p.expect ('up ([0-9]+) days?,.*?,\s+([0-9]+) users?,\s+load averages?: ([0-9]+\.[0-9][0-9]), ([0-9]+\.[0-9][0-9]), ([0-9]+\.[0-9][0-9])')

duration, users, av1, av5, av15 = p.match.groups()

print '%s days, %s users, %s (1 min), %s (5 min), %s (15 min)' % (
    duration, users, av1, av5, av15)


