#!/usr/bin/env python
import pexpect
p = pexpect.spawn('cat')
p.interact()
