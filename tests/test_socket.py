#!/usr/bin/env python
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
import pexpect
from pexpect import socket_pexpect
import unittest
from . import PexpectTestCase
import os
import socket
import sys

class ExpectTestCase(PexpectTestCase.PexpectTestCase):
    def setUp(self):
        print(self.id())
        PexpectTestCase.PexpectTestCase.setUp(self)

    def test_socket (self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('rainmaker.wunderground.com', 23))
        session = socket_pexpect.socket_spawn(sock.fileno(), timeout=10)
        session.expect('Press Return to continue:')
        motd = """\
------------------------------------------------------------------------------
*               Welcome to THE WEATHER UNDERGROUND telnet service!            *
------------------------------------------------------------------------------
*                                                                            *
*   National Weather Service information provided by Alden Electronics, Inc. *
*    and updated each minute as reports come in over our data feed.          *
*                                                                            *
*   **Note: If you cannot get past this opening screen, you must use a       *
*   different version of the "telnet" program--some of the ones for IBM      *
*   compatible PC's have a bug that prevents proper connection.              *
*                                                                            *
*           comments: jmasters@wunderground.com                              *
------------------------------------------------------------------------------
""".replace('\n', '\n\r') + "\r\n"
        self.assertEqual(session.before, motd)

    def test_timeout(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('rainmaker.wunderground.com', 23))
        session = socket_pexpect.socket_spawn(sock.fileno(), timeout=10)
        result_list = ['Bogus response', pexpect.TIMEOUT]
        result = session.expect(result_list)
        self.assertEqual(result, result_list.index(pexpect.TIMEOUT))

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ExpectTestCase, 'test')
