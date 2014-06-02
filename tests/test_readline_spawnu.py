#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pexpect

ECHO = pexpect.which('echo')

"""
Test using readline() with spawnu objects. This fails with a TypeError on older
versions of pexpect because bytes are used for line endings rather than
strings.
"""
child = pexpect.spawnu(ECHO, [ "foobar"])
foobar = child.readline()
