'''This is like pexpect, but it will work with serial port that you
pass it. You are reponsible for opening and close the serial port.
This allows you to use Pexpect with Serial port which pyserial supports.

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

from .spawnbase import SpawnBase
from .exceptions import ExceptionPexpect

__all__ = ['serial_spawn']

class SerialSpawn(SpawnBase):
    '''This is like pexpect.spawn but allows you to supply a serial created by
    pyserial.'''

    def __init__ (self, ser, args=None, timeout=30, maxread=2000, searchwindowsize=None,
                  logfile=None, encoding=None, codec_errors='strict'):
        '''This takes a serial of pyserial as input. Please make sure the serial is open
        before creating SerialSpawn.'''

        self.ser = ser
        if not ser.isOpen():
            raise ExceptionPexpect('serial port is not ready')

        self.args = None
        self.command = None
        SpawnBase.__init__(self, timeout, maxread, searchwindowsize, logfile,
                           encoding=encoding, codec_errors=codec_errors)
        self.own_fd = False
        self.closed = False
        self.name = '<serial port %s>' % ser.port

    def close (self):
        """Close the serial port.

        Calling this method a second time does nothing.
        """
        if not self.ser.isOpen():
            return

        self.flush()
        self.ser.close()
        self.closed = True

    def isalive (self):
        '''This checks if the serial port is still valid.'''
        return self.ser.isOpen()

    def read_nonblocking(self, size=1, timeout=None):
        s = self.ser.read(size)
        s = self._decoder.decode(s, final=False)
        self._log(s, 'read')
        return s

    def send(self, s):
        "Write to serial, return number of bytes written"
        s = self._coerce_send_string(s)
        self._log(s, 'send')

        b = self._encoder.encode(s, final=False)
        return self.ser.write(b)

    def sendline(self, s):
        "Write to fd with trailing newline, return number of bytes written"
        s = self._coerce_send_string(s)
        return self.send(s + self.linesep)

    def write(self, s):
        "Write to serial, return None"
        self.send(s)

    def writelines(self, sequence):
        "Call self.write() for each item in sequence"
        for s in sequence:
            self.write(s)
