#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from __future__ import print_function
from __future__ import unicode_literals

import os
import pexpect
import unittest
import sys
from . import PexpectTestCase


class InteractTestCase (PexpectTestCase.PexpectTestCase):
    def setUp(self):
        super(InteractTestCase, self).setUp()
        self.env = env = os.environ.copy()

        # Ensure 'import pexpect' works in subprocess interact*.py
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = os.pathsep.join((self.project_dir,
                                                    env['PYTHONPATH']))
        else:
            env['PYTHONPATH'] = self.project_dir

        self.interact_py = ' '.join((sys.executable,
                                     'interact.py',))
        self.interact_ucs_py = ' '.join((sys.executable,
                                         'interact_unicode.py',))

    def test_interact_escape(self):
        " Ensure `escape_character' value exits interactive mode. "
        p = pexpect.spawn(self.interact_py, timeout=5, env=self.env)
        p.expect('<in >')
        p.sendcontrol(']')  # chr(29), the default `escape_character'
                            # value of pexpect.interact().
        p.expect_exact('Escaped interact')
        p.expect(pexpect.EOF)
        assert not p.isalive()
        assert p.exitstatus == 0

    def test_interact_spawn_eof(self):
        " Ensure subprocess receives EOF and exit. "
        p = pexpect.spawn(self.interact_py, timeout=5, env=self.env)
        p.expect('<in >')
        p.sendline(b'alpha')
        p.sendline(b'beta')
        p.expect(b'<out>alpha')
        p.expect(b'<out>beta')
        p.sendeof()
        p.expect_exact('<eof>')
        p.expect_exact('Escaped interact')
        p.expect(pexpect.EOF)
        assert not p.isalive()
        assert p.exitstatus == 0

    def test_interact_spawnu_eof(self):
        " Ensure subprocess receives unicode, EOF, and exit. "
        p = pexpect.spawnu(self.interact_ucs_py, timeout=5, env=self.env)
        p.expect('<in >')
        p.sendline('ɑlpha')
        p.sendline('Βeta')
        p.expect('<out>ɑlpha')
        p.expect('<out>Βeta')
        p.sendeof()
        p.expect_exact('<eof>')
        p.expect_exact('Escaped interact')
        p.expect(pexpect.EOF)
        assert not p.isalive()
        assert p.exitstatus == 0

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(InteractTestCase, 'test')

