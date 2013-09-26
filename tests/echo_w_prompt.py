# -*- coding: utf-8 -*-
from __future__ import print_function

try:
    raw_input
except NameError:
    raw_input = input

while True:
    a = raw_input('<in >')
    print('<out>', a, sep='')