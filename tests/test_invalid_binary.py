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
import unittest
from . import PexpectTestCase
import os
import stat
import tempfile

class InvalidBinaryChars(PexpectTestCase.PexpectTestCase):

    def test_invalid_binary(self):
        '''This tests that we correctly handle the case where we attempt to
           spawn a child process but the exec call fails'''

        # Create a file that should fail the exec call
        dirpath = tempfile.mkdtemp()
        fullpath = os.path.join(dirpath, "test")

        test = os.open(fullpath, os.O_RDWR | os.O_CREAT)
        os.write(test, os.urandom(1024)) # Contents shouldn't matter
        os.close(test)

        # Make it executable
        st = os.stat(fullpath)
        os.chmod(fullpath, st.st_mode | stat.S_IEXEC)

        # TODO Verify this does what is intended on Windows
        try:
            child = pexpect.spawn(fullpath)
            # If we get here then an OSError was not raised
            child.close()
            os.unlink(fullpath)
            os.rmdir(dirpath)
            raise AssertionError("OSError was not raised")
        except OSError:
            # This is what should happen
            pass

        os.unlink(fullpath)
        os.rmdir(dirpath)

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(InvalidBinaryChars,'test')

