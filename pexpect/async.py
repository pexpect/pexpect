import asyncio
import errno

from pexpect import EOF

@asyncio.coroutine
def expect_async(expecter, timeout=None):
    # First process data that was previously read - if it maches, we don't need
    # async stuff.
    previously_read = expecter.spawn.buffer
    expecter.spawn.buffer = expecter.spawn.string_type()
    idx = expecter.new_data(previously_read)
    if idx is not None:
        return idx

    transport, pw = yield from asyncio.get_event_loop()\
        .connect_read_pipe(lambda: PatternWaiter(expecter), expecter.spawn)

    try:
        return (yield from asyncio.wait_for(pw.fut, timeout))
    except asyncio.TimeoutError as e:
        transport.pause_reading()
        return expecter.timeout(e)

class PatternWaiter(asyncio.Protocol):
    def __init__(self, expecter):
        self.expecter = expecter
        self.fut = asyncio.Future()
    
    def found(self, result):
        if not self.fut.done():
            self.fut.set_result(result)
    
    def error(self, exc):
        if not self.fut.done():
            self.fut.set_exception(exc)
    
    def data_received(self, data):
        spawn = self.expecter.spawn
        s = spawn._decoder.decode(data)
        spawn._log(s, 'read')

        if self.fut.done():
            spawn.buffer += data
            return

        try:
            index = self.expecter.new_data(data)
            if index is not None:
                # Found a match
                self.found(index)
        except Exception as e:
            self.expecter.errored()
            self.error(e)
    
    def eof_received(self):
        # N.B. If this gets called, async will close the pipe (the spawn object)
        # for us
        try:
            self.expecter.spawn.flag_eof = True
            index = self.expecter.eof()
        except EOF as e:
            self.error(e)
        else:
            self.found(index)
    
    def connection_lost(self, exc):
        if isinstance(exc, OSError) and exc.errno == errno.EIO:
            # We may get here without eof_received being called, e.g on Linux
            self.eof_received()
        elif exc is not None:
            self.error(exc)
