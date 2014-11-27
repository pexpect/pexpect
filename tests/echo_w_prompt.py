# -*- coding: utf-8 -*-
from __future__ import print_function
import codecs
import sys

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)


try:
    raw_input
except NameError:
    raw_input = input

while True:
    try:
        a = raw_input('<in >')
    except EOFError:
        print('<eof>')
        break
    print('<out>', a, sep='')
