'''
This currently just holds some notes.
This is not expected to be working code.

$Revision: 120 $
$Date: 2002-11-27 11:13:04 -0800 (Wed, 27 Nov 2002) $

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

import tty, termios, sys

def getkey():
    file = sys.stdin.fileno()
    mode = termios.tcgetattr(file)
    try:
        tty.setraw(file, termios.TCSANOW)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(file, termios.TCSANOW, mode)
    return ch

def test_typing ():
    s = screen (10,10)
    while 1:
        ch = getkey()
        s.type(ch)
        print str(s)
        print

