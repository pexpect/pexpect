#!/usr/bin/env python
"""This displays uptime information using uptime.
A bit redundant perhaps, but it demonstrates expecting for a
regular expression that uses subgroups.
"""

import pexpect
import re

p = pexpect.spawn ('uptime')
p.expect ('up ([0-9]+) days, ..:..,\s+([0-9]+) users,\s+load average[s]*: ([0-9]+\.[0-9][0-9]), ([0-9]+\.[0-9][0-9]), ([0-9]+\.[0-9][0-9])')

days, users, av1, av5, av15 = p.match.groups()

print '%s days, %s users, %s (1 min), %s (5 min), %s (15 min)' % (
    days, users, av1, av5, av15)
