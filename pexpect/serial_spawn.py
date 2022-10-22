import os
import sys
import time
import threading
from pexpect.fdpexpect import SpawnBase
from pexpect.exceptions import EOF, TIMEOUT, ExceptionPexpect

PY3 = (sys.version_info[0] >= 3)


class SerialSpawn(SpawnBase):
    '''This is a serial interface class interface for Pexpect. Use this class to
    control an existing python serial connection. '''
    def __init__(self, ser, args=None, **kwargs):
        if not ser.is_open:
            raise ExceptionPexpect('serial port is not ready')
        super().__init__(None, **kwargs)
        self.ser = ser
        self.name = f'<serial port {ser.port}>'
        self.closed = False
        self.interacting = threading.Event()

    def close(self):
        if not self.ser.is_open:
            return
        self.flush()
        self.ser.close()
        self.closed = True

    def isalive(self):
        return self.ser.is_open

    def send(self, s):
        s = self._coerce_send_string(s)
        self._log(s, 'send')
        b = self._encoder.encode(s, final=False)
        return self.ser.write(b)
    
    def read_nonblocking(self, size=1, timeout=-1):
        if not self.isalive():
            raise EOF('End Of File (EOF).')
        if timeout and timeout < 0:
            timeout = self.timeout
        if timeout and timeout < 0:
            timeout = 0
        self.ser.timeout = timeout
        s = self.ser.read(n)
        s = self._decoder.decode(s, final=False)
        self._log(s, 'read')
        return s

    def _interact_output_loop(self, escape_character=chr(29), input_filter=None, output_filter=None):
        while self.interacting.is_set():
            if not self.isalive():
                self.interacting.set()
            try:
                data = self.read_nonblocking(size=1000)
                if output_filter:
                    data = output_filter(data)
                self.write_to_stdout(data)
                self.stdout.flush()
            except:
                pass

    def _interact_input_loop(self, escape_character=chr(29), input_filter=None):
        while self.interacting.is_set():
            data = os.read(self.stdin.fileno(), 1000)
            print(data)
            i = -1
            if escape_character is not None:
                i = data.rfind(escape_character)
            data = self._decoder.decode(data, final=False)
            if input_filter:
                data = input_filter(data)
            if i != -1:
                data = data[:i]
                self.interacting.clear()
            if data:
                self.send(data)

    def interact(self, escape_character=chr(29), input_filter=None, output_filter=None):
        # Flush buffer to stdout...
        self.write_to_stdout(self.buffer)
        self.stdout.flush()
        # Fix escape character encoding
        if escape_character is not None and PY3:
            escape_character = escape_character.encode('latin-1')
        # Set the interacting event and start the input thread
        self.interacting.set()
        input_thread = threading.Thread(target=self._interact_input_loop, args=(escape_character, input_filter))
        input_thread.start()
        # Run output loop in this thread
        self._interact_output_loop(escape_character, input_filter, output_filter)
        # Join input thread on exit...
        input_thread.join()
