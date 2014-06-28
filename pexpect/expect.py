import time

class Expecter(object):
    def __init__(self, spawn, searcher, searchwindowsize=-1):
        self.spawn = spawn
        self.searcher = searcher
        if searchwindowsize == -1:
            searchwindowsize = spawn.searchwindowsize
        self.searchwindowsize = searchwindowsize
    
    def new_data(self, data):
        spawn = self.spawn
        searcher = self.searcher

        incoming = spawn.buffer + data
        freshlen = len(data)
        index = searcher.search(incoming, freshlen, self.searchwindowsize)
        if index >= 0:
            spawn.buffer = incoming[searcher.end:]
            spawn.before = incoming[: searcher.start]
            spawn.after = incoming[searcher.start: searcher.end]
            spawn.match = searcher.match
            spawn.match_index = index
            # Found a match
            return index
    
        spawn.buffer = incoming
    
    def eof(self, err=None):
        spawn = self.spawn
        from . import EOF

        spawn.before = spawn.buffer
        spawn.buffer = spawn.string_type()
        spawn.after = EOF
        index = self.searcher.eof_index
        if index >= 0:
            spawn.match = EOF
            spawn.match_index = index
            return index
        else:
            spawn.match = None
            spawn.match_index = None
            msg = str(spawn)
            if err is not None:
                msg = str(err) + '\n' + msg
            raise EOF(msg)
    
    def timeout(self, err=None):
        spawn = self.spawn
        from . import TIMEOUT

        spawn.before = spawn.buffer
        spawn.after = TIMEOUT
        index = self.searcher.timeout_index
        if index >= 0:
            spawn.match = TIMEOUT
            spawn.match_index = index
            return index
        else:
            spawn.match = None
            spawn.match_index = None
            msg = str(spawn)
            if err is not None:
                msg = str(err) + '\n' + msg
            raise TIMEOUT(msg)

    def errored(self):
        spawn = self.spawn
        spawn.before = spawn.buffer
        spawn.after = None
        spawn.match = None
        spawn.match_index = None
    
    def expect_loop(self, timeout=-1):
        """Blocking expect"""
        spawn = self.spawn
        from . import EOF, TIMEOUT

        if timeout == -1:
            timeout = self.spawn.timeout
        if timeout is not None:
            end_time = time.time() + timeout

        try:
            incoming = spawn.buffer
            spawn.buffer = spawn.string_type()  # Treat buffer as new data
            while True:
                idx = self.new_data(incoming)
                # Keep reading until exception or return.
                if idx is not None:
                    return idx
                # No match at this point
                if (timeout is not None) and (timeout < 0):
                    return self.timeout()
                # Still have time left, so read more data
                incoming = spawn.read_nonblocking(spawn.maxread, timeout)
                time.sleep(0.0001)
                if timeout is not None:
                    timeout = end_time - time.time()
        except EOF as e:
            return self.eof(e)
        except TIMEOUT as e:
            return self.timeout(e)
        except:
            self.errored()
            raise