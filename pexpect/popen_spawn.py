"""Spawn interface using subprocess.Popen
"""
import os
import threading
import subprocess
import sys

try:
    from queue import Queue  # Python 3
except ImportError:
    from Queue import Queue  # Python 2

from .spawnbase import SpawnBase, SpawnBaseUnicode

class PopenSpawn(SpawnBase):
    def __init__(self, cmd, timeout=30, maxread=2000, searchwindowsize=None,
                 logfile=None, cwd=None,  env=None):
        super(PopenSpawn, self).__init__(timeout=timeout, maxread=maxread,
                searchwindowsize=searchwindowsize, logfile=logfile)
                
        kwargs = dict(bufsize=0, stdin=subprocess.PIPE,
                      stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
                      cwd=cwd, env=env)

        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs['startupinfo'] = startupinfo
            kwargs['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP

        self.proc = subprocess.Popen(cmd, **kwargs)
        self._buf = ''

        self._read_queue = Queue()
        self._read_thread = threading.Thread(target=self._read_incoming)
        self._read_thread.setDaemon(True)
        self._read_thread.start()

    def read_nonblocking(self, n):
        orig = len(self._buf)
        while 1:
            try:
                self._buf += self._read_queue.get_nowait()
            except Queue.Empty:
                return
            else:
                if len(self._buf) - orig >= n:
                    return

    def _read_incoming(self):
        """Run in a thread to move output from a pipe to a queue."""
        while 1:
            buf = os.read(self.proc.stdout.fileno(), 1024)
            self._read_queue.put(buf)

    def readline(self):
        while not '\n' in self._buf:
            self.read_nonblocking(1024)
            ind = self._buf.index('\n')
            ret, self._buf = self._buf[:ind], self._buf[ind:]
            return ret

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
        self._log(s, 'send')
        return self._send(s)        

    def sendline(self, line):
        return self.send(line + '\n')

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

class PopenSpawnUnicode(SpawnBaseUnicode, PopenSpawn):
    def _send(self, s):
        super(PopenSpawnUnicode, self)._send(s.encode(self.encoding, self.errors))
