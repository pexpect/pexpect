#!/usr/bin/env python
import sys

lines = sys.stdin.readlines()
for line in lines:
    sys.stdout.write ('#' + line)
