'''This is like fdpexpect, but it will work with sockets. You are responsible
for opening and closing the socket.

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

import errno
import select
import sys
import time

from .fdpexpect import fdspawn
from .exceptions import TIMEOUT

__all__ = ['socket_pexpect']


class socket_spawn(fdspawn):
    '''This is like pexpect.fdspawn but it works with sockets.'''

    def read_nonblocking(self, size=1, timeout=-1):
        '''The read_nonblocking method of fdspawn assumes that the file
        will never block. This is not the case for sockets. So we use
        select to implement the timeout.'''
        if timeout == -1:
            timeout = self.timeout
        rlist = [self.child_fd]
        wlist = []
        xlist = []
        rlist, wlist, xlist = self.__select(rlist, wlist, xlist, timeout)
        if self.child_fd not in rlist:
            raise TIMEOUT('Timeout exceeded.')
        return super(fdspawn, self).read_nonblocking(size)

    def __select(self, iwtd, owtd, ewtd, timeout=None):

        '''This is a wrapper around select.select() that ignores signals. If
        select.select raises a select.error exception and errno is an EINTR
        error then it is ignored. Mainly this is used to ignore sigwinch
        (terminal resize). '''

        # if select() is interrupted by a signal (errno==EINTR) then
        # we loop back and enter the select() again.
        if timeout is not None:
            end_time = time.time() + timeout
        while True:
            try:
                return select.select(iwtd, owtd, ewtd, timeout)
            except select.error:
                err = sys.exc_info()[1]
                if err.args[0] == errno.EINTR:
                    # if we loop back we have to subtract the
                    # amount of time we already waited.
                    if timeout is not None:
                        timeout = end_time - time.time()
                        if timeout < 0:
                            return [], [], []
                else:
                    # something else caused the select.error, so
                    # this actually is an exception.
                    raise
