"""Spawn interface using subprocess.Popen
"""
import os
import threading
import subprocess
import sys
import time
import signal
import shlex

try:
    from queue import Queue, Empty  # Python 3
except ImportError:
    from Queue import Queue, Empty  # Python 2

from .spawnbase import SpawnBase, PY3
from .exceptions import EOF

class PopenSpawn(SpawnBase):
    if PY3:
        crlf = '\n'.encode('ascii')
    else:
        crlf = '\n'

    def __init__(self, cmd, timeout=30, maxread=2000, searchwindowsize=None,
                 logfile=None, cwd=None,  env=None, encoding=None,
                 codec_errors='strict'):
        super(PopenSpawn, self).__init__(timeout=timeout, maxread=maxread,
                searchwindowsize=searchwindowsize, logfile=logfile,
                encoding=encoding, codec_errors=codec_errors)

        kwargs = dict(bufsize=0, stdin=subprocess.PIPE,
                      stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
                      cwd=cwd, env=env)

        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs['startupinfo'] = startupinfo
            kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP

        if not isinstance(cmd, (list, tuple)):
            cmd = shlex.split(cmd)

        self.proc = subprocess.Popen(cmd, **kwargs)
        self.closed = False
        self._buf = ''

        self._read_queue = Queue()
        self._read_thread = threading.Thread(target=self._read_incoming)
        self._read_thread.setDaemon(True)
        self._read_thread.start()

    def read_nonblocking(self, size, timeout):
        if self.closed:
            raise ValueError('I/O operation on closed file.')
        elif self.flag_eof:
            self.closed = True
            raise EOF('End Of File (EOF).')

        if timeout == -1:
            timeout = self.timeout
        elif timeout is None:
            timeout = 1e6

        t0 = time.time()
        buf = self.string_type()
        while (time.time() - t0) < timeout and size and len(buf) < size:
            try:
                incoming = self._read_queue.get_nowait()
            except Empty:
                break
            else:
                if incoming is None:
                    self.flag_eof = True
                    raise EOF('End of File')

                buf += self._decoder.decode(incoming, final=False)

        if len(buf) > size:
            self.buffer = buf[size:]
            buf = buf[:size]

        self._log(buf, 'read')
        return buf

    def _read_incoming(self):
        """Run in a thread to move output from a pipe to a queue."""
        fileno = self.proc.stdout.fileno()
        while 1:
            buf = b''
            try:
                buf = os.read(fileno, 1024)
            except OSError as e:
                self._log(e, 'read')

            if not buf:
                self._read_queue.put(None)
                return

            self._read_queue.put(buf)
            time.sleep(0.001)

    def write(self, s):
        '''This is similar to send() except that there is no return value.
        '''
        self.send(s)

    def writelines(self, sequence):
        '''This calls write() for each element in the sequence.

        The sequence can be any iterable object producing strings, typically a
        list of strings. This does not add line separators. There is no return
        value.
        '''
        for s in sequence:
            self.send(s)

    def _send(self, s):
        return self.proc.stdin.write(s)

    def send(self, s):
        s = self._coerce_send_string(s)
        self._log(s, 'send')

        return self._send(s)

    def sendline(self, s=''):
        '''Wraps send(), sending string ``s`` to child process, with os.linesep
        automatically appended. Returns number of bytes written. '''

        n = self.send(s)
        return n + self.send(self.linesep)

    def wait(self):
        status = self.proc.wait()
        if status >= 0:
            self.exitstatus = status
            self.signalstatus = None
        else:
            self.exitstatus = None
            self.signalstatus = -status
        self.terminated = True
        return status

    def kill(self, sig):
        if sys.platform == 'win32':
            if sig in [signal.SIGINT, signal.CTRL_C_EVENT]:
                sig = signal.CTRL_C_EVENT
            elif sig in [signal.SIGBREAK, signal.CTRL_BREAK_EVENT]:
                sig = signal.CTRL_BREAK_EVENT
            else:
                sig = signal.SIGTERM

        os.kill(self.proc.pid, sig)

    def sendeof(self):
        self.proc.stdin.close()
