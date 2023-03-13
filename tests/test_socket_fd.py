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
from pexpect import fdpexpect
import unittest
from . import test_socket
import multiprocessing
import os
import signal
import socket
import time
import errno


class SocketServerError(Exception):
    pass


class ExpectTestCase(test_socket.ExpectTestCase):
    """ duplicate of test_socket, but using fdpexpect rather than socket_expect """

    def spawn(self, socket, timeout=30, use_poll=False):
        return fdpexpect.fdspawn(socket.fileno(), timeout=timeout, use_poll=use_poll)

    def test_not_int(self):
        with self.assertRaises(pexpect.ExceptionPexpect):
            session = fdpexpect.fdspawn('bogus', timeout=10)

    def test_not_file_descriptor(self):
        with self.assertRaises(pexpect.ExceptionPexpect):
            session = fdpexpect.fdspawn(-1, timeout=10)

    def test_fileobj(self):
        sock = socket.socket(self.af, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        session = fdpexpect.fdspawn(sock, timeout=10) # Should get the fileno from the socket
        session.expect(self.prompt1)
        session.close()
        assert not session.isalive()
        session.close()  # Smoketest - should be able to call this again


if __name__ == '__main__':
    unittest.main()

suite = unittest.TestLoader().loadTestsFromTestCase(ExpectTestCase)
