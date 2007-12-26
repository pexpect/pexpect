#!/usr/bin/env python
import sys, time
while True:
    x = raw_input ()
    time.sleep(1) # without this delay the test would fail about 75% of the time. Why?
    print x.swapcase()
    sys.stdout.flush()
