import asyncio

from pexpect import EOF, searcher_re

@asyncio.coroutine
def expect_async(spawn, pattern):
    searcher = searcher_re(spawn.compile_pattern_list(pattern))

    def protocol_factory():
        return PatternWaiter(spawn, searcher)    
    transport, pw = yield from asyncio.get_event_loop()\
                        .connect_read_pipe(protocol_factory, spawn)
    
    return (yield from pw.fut)

class PatternWaiter(asyncio.Protocol):
    def __init__(self, spawn, searcher):
        self.spawn = spawn
        self.searcher = searcher
        self.fut = asyncio.Future()
    
    def found(self, result):
        if not self.fut.done():
            self.fut.set_result(result)
    
    def error(self, exc):
        if not self.fut.done():
            self.fut.set_exception(exc)
    
    def data_received(self, data):
        spawn = self.spawn
        s = spawn._coerce_read_string(data)
        spawn._log(s, 'read')
        
        searcher = self.searcher
        try:
            incoming = spawn.buffer + s
            freshlen = len(s)
            index = searcher.search(incoming, freshlen)
            if index >= 0:
                spawn.buffer = incoming[searcher.end:]
                spawn.before = incoming[: searcher.start]
                spawn.after = incoming[searcher.start: searcher.end]
                spawn.match = searcher.match
                spawn.match_index = index
                # Found a match
                self.found(index)
        except Exception as e:
            spawn.before = incoming
            spawn.after = None
            spawn.match = None
            spawn.match_index = None
            self.error(e)
    
        spawn.buffer = incoming
    
    def eof_received(self):
        spawn = self.spawn
        spawn.before = spawn.buffer
        spawn.buffer = spawn.string_type()
        spawn.after = EOF
        index = self.searcher.eof_index
        if index >= 0:
            spawn.match = EOF
            spawn.match_index = index
            self.found(index)
        else:
            spawn.match = None
            spawn.match_index = None
            self.error(EOF(str(spawn)))

    