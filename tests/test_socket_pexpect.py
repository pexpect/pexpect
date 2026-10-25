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
import socket

def open_file_socket(filename):
    read_socket, write_socket = socket.socketpair()
    with open(filename, "rb") as file:
        write_socket.sendall(file.read())
    write_socket.close()
    return read_socket

class ExpectTestCase(PexpectTestCase.PexpectTestCase):
    def setUp(self):
        print(self.id())
        PexpectTestCase.PexpectTestCase.setUp(self)

    def test_socket (self):
        socket = open_file_socket('TESTDATA.txt')
        s = socket_pexpect.SocketSpawn(socket)
        s.expect(b'This is the end of test data:')
        s.expect(pexpect.EOF)
        self.assertEqual(s.before, b' END\n')

    def test_maxread (self):
        socket = open_file_socket('TESTDATA.txt')
        s = socket_pexpect.SocketSpawn(socket)
        s.maxread = 100
        s.expect('2')
        s.expect ('This is the end of test data:')
        s.expect (pexpect.EOF)
        self.assertEqual(s.before, b' END\n')

    def test_socket_isalive (self):
        socket = open_file_socket('TESTDATA.txt')
        s = socket_pexpect.SocketSpawn(socket)
        assert s.isalive()
        s.close()
        assert not s.isalive(), "Should not be alive after close()"

    def test_socket_isatty (self):
        socket = open_file_socket('TESTDATA.txt')
        s = socket_pexpect.SocketSpawn(socket)
        assert not s.isatty()
        s.close()

    def test_socket_unicode(self):
        for method in ('expect', 'expect_exact'):
            with self.subTest(method=method):
                read_socket, write_socket = socket.socketpair()
                self.addCleanup(read_socket.close)
                self.addCleanup(write_socket.close)
                write_socket.sendall(u'before caf\u00e9 after'.encode('utf-8'))
                write_socket.shutdown(socket.SHUT_WR)
                s = socket_pexpect.SocketSpawn(read_socket, encoding='utf-8',
                                               maxread=1, timeout=1)
                self.assertEqual(getattr(s, method)(u'caf\u00e9'), 0)
                self.assertEqual(s.before, u'before ')
                self.assertEqual(s.after, u'caf\u00e9')
                s.expect(pexpect.EOF)
                self.assertEqual(s.before, u' after')

    def test_read_unicode_split_character(self):
        read_socket, write_socket = socket.socketpair()
        self.addCleanup(read_socket.close)
        self.addCleanup(write_socket.close)
        s = socket_pexpect.SocketSpawn(read_socket, encoding='utf-8')
        write_socket.sendall(b'\xc3')
        self.assertEqual(s.read_nonblocking(size=1, timeout=1), u'')
        self.assertFalse(s.flag_eof)
        write_socket.sendall(b'\xa9')
        self.assertEqual(s.read_nonblocking(size=1, timeout=1), u'\u00e9')
        write_socket.shutdown(socket.SHUT_WR)
        with self.assertRaises(pexpect.EOF):
            s.read_nonblocking(size=1, timeout=1)
        self.assertTrue(s.flag_eof)

    def test_read_unicode_strict_errors(self):
        read_socket, write_socket = socket.socketpair()
        self.addCleanup(read_socket.close)
        self.addCleanup(write_socket.close)
        read_socket.settimeout(0.25)
        s = socket_pexpect.SocketSpawn(read_socket, encoding='utf-8')
        write_socket.sendall(b'\xff')
        with self.assertRaises(UnicodeDecodeError):
            s.read_nonblocking(size=1, timeout=1)
        self.assertEqual(read_socket.gettimeout(), 0.25)

    def test_read_unicode_replace_errors(self):
        read_socket, write_socket = socket.socketpair()
        self.addCleanup(read_socket.close)
        self.addCleanup(write_socket.close)
        s = socket_pexpect.SocketSpawn(read_socket, encoding='utf-8',
                                       codec_errors='replace')
        write_socket.sendall(b'\xff')
        self.assertEqual(s.read_nonblocking(size=1, timeout=1), u'\ufffd')


if __name__ == '__main__':
    unittest.main()

suite = unittest.TestLoader().loadTestsFromTestCase(ExpectTestCase)
