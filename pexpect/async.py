import asyncio

from pexpect import EOF, searcher_re
from pexpect.expect import Expecter

@asyncio.coroutine
def expect_async(spawn, pattern):
    searcher = searcher_re(spawn.compile_pattern_list(pattern))

    def protocol_factory():
        return PatternWaiter(Expecter(spawn, searcher))
    transport, pw = yield from asyncio.get_event_loop()\
                        .connect_read_pipe(protocol_factory, spawn)
    
    return (yield from pw.fut)

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
        s = spawn._coerce_read_string(data)
        spawn._log(s, 'read')

        try:
            index = self.expecter.new_data(data)
            if index is not None:
                # Found a match
                self.found(index)
        except Exception as e:
            self.expecter.errored()
            self.error(e)
    
    def eof_received(self):
        try:
            index = self.expecter.eof()
        except EOF as e:
            self.error(e)
        else:
            self.found(index)