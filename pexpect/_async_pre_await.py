"""Implementation of coroutines without using ``async def``/``await`` keywords.

``@asyncio.coroutine`` and ``yield from`` are  used here instead.
"""
import asyncio
import errno
import signal
import os

from pexpect import EOF

_loop_getter = asyncio.get_event_loop

@asyncio.coroutine
def expect_async(expecter, timeout=None):
    # First process data that was previously read - if it maches, we don't need
    # async stuff.
    idx = expecter.existing_data()
    if idx is not None:
        return idx

    if expecter.spawn.has_eof:
        return expecter.eof()

    if not expecter.spawn.async_pw_transport:
        pw = PatternWaiter()
        pw.set_expecter(expecter)
        transport, pw = yield from _loop_getter().connect_read_pipe(
            lambda: pw, expecter.spawn
        )
        expecter.spawn.async_pw_transport = pw, transport
    else:
        pw, transport = expecter.spawn.async_pw_transport
        pw.set_expecter(expecter)
        transport.resume_reading()
    try:
        return (yield from asyncio.wait_for(pw.fut, timeout))
    except asyncio.TimeoutError as e:
        transport.pause_reading()
        return expecter.timeout(e)


@asyncio.coroutine
def repl_run_command_async(repl, command, cmdlines, timeout=-1):
    res = []
    yield from repl.child.sendline(cmdlines[0], async_=True)
    for line in cmdlines[1:]:
        yield from repl._expect_prompt(timeout=timeout, async_=True)
        res.append(repl.child.before)
        yield from repl.child.sendline(line, async_=True)

    # Command was fully submitted, now wait for the next prompt
    prompt_idx = yield from repl._expect_prompt(timeout=timeout, async_=True)
    if prompt_idx == 1:
        # We got the continuation prompt - command was incomplete
        repl.child.kill(signal.SIGINT)
        yield from repl._expect_prompt(timeout=1, async_=True)
        raise ValueError("Continuation prompt found - input was incomplete\n"
                             + command)
    return "".join(res + [repl.child.before])

@asyncio.coroutine
def spawn__waitnoecho_async(spawn, timeout, end_time):
    while True:
        if not spawn.getecho():
            return True
        if timeout < 0 and timeout is not None:
            return False
        if timeout is not None:
            timeout = end_time - time.time()
        yield from asyncio.sleep(0.1)

@asyncio.coroutine
def spawn__write_async(spawn, s):
    yield from spawn.send(s, async_=True)

@asyncio.coroutine
def spawn__writelines_async(spawn, sequence):
    for s in sequence:
        yield from spawn.write(s, async_=True)

@asyncio.coroutine
def spawn__send_async(spawn, s):
    if spawn.delaybeforesend is not None:
        yield from asyncio.sleep(spawn.delaybeforesend)

    s = spawn._coerce_send_string(s)
    spawn._log(s, 'send')

    b = spawn._encoder.encode(s, final=False)
    return os.write(spawn.child_fd, b)

@asyncio.coroutine
def spawn__terminate_async(spawn, force=False):
    if not spawn.isalive():
        return True

    try:
        spawn.kill(signal.SIGHUP)
        yield from asyncio.sleep(spawn.delayafterterminate)
        if not spawn.isalive():
            return True
        spawn.kill(signal.SIGCONT)
        yield from asyncio.sleep(spawn.delayafterterminate)
        if not spawn.isalive():
            return True
        spawn.kill(signal.SIGINT)
        yield from asyncio.sleep(spawn.delayafterterminate)
        if not spawn.isalive():
            return True
        if force:
            spawn.kill(signal.SIGKILL)
            yield from asyncio.sleep(spawn.delayafterterminate)
            if not spawn.isalive():
                return True
            else:
                return False
        return False
    except OSError:
        # I think there are kernel timing issues that sometimes cause
        # this to happen. I think isalive() reports True, but the
        # process is dead to the kernel.
        # Make one last attempt to see if the kernel is up to date.
        yield from asyncio.sleep(spawn.delayafterterminate)
        if not spawn.isalive():
            return True
        else:
            return False

@asyncio.coroutine
def spawnbase__read_async(spawn, size):

    if size == 0:
        return spawn.string_type()
    if size < 0:
        # delimiter default is EOF
        yield from spawn.expect(spawn.delimiter, async_=True)
        return spawn.before

    # I could have done this more directly by not using expect(), but
    # I deliberately decided to couple read() to expect() so that
    # I would catch any bugs early and ensure consistent behavior.
    # It's a little less efficient, but there is less for me to
    # worry about if I have to later modify read() or expect().
    # Note, it's OK if size==-1 in the regex. That just means it
    # will never match anything in which case we stop only on EOF.
    cre = re.compile(spawn._coerce_expect_string('.{%d}' % size), re.DOTALL)
    # delimiter default is EOF
    index = yield from spawn.expect([cre, spawn.delimiter], async_=True)
    if index == 0:
        ### FIXME spawn.before should be ''. Should I assert this?
        return spawn.after
    return spawn.before

@asyncio.coroutine
def spawnbase__readline_async(spawn, size):
    '''This reads and returns one entire line. The newline at the end of
    line is returned as part of the string, unless the file ends without a
    newline. An empty string is returned if EOF is encountered immediately.
    This looks for a newline as a CR/LF pair (\\r\\n) even on UNIX because
    this is what the pseudotty device returns. So contrary to what you may
    expect you will receive newlines as \\r\\n.

    If the size argument is 0 then an empty string is returned. In all
    other cases the size argument is ignored, which is not standard
    behavior for a file-like object. '''

    if size == 0:
        return spawn.string_type()
    # delimiter default is EOF
    index = yield from spawn.expect([spawn.crlf, spawn.delimiter], async_=True)
    if index == 0:
        return spawn.before + spawn.crlf
    else:
        return spawn.before

@asyncio.coroutine
def spawnbase__readlines_async(spawn, sizehint):
    '''This reads until EOF using readline() and returns a list containing
    the lines thus read. The optional 'sizehint' argument is ignored.
    Remember, because this reads until EOF that means the child
    process should have closed its stdout. If you run this method on
    a child that is still running with its stdout open then this
    method will block until it timesout.'''

    lines = []
    while True:
        line = yield from spawn.readline(async_=True)
        if not line:
            break
        lines.append(line)
    return lines

class PatternWaiter(asyncio.Protocol):
    transport = None

    def set_expecter(self, expecter):
        self.expecter = expecter
        self.fut = asyncio.Future()

    def found(self, result):
        if not self.fut.done():
            self.fut.set_result(result)
            self.transport.pause_reading()

    def error(self, exc):
        if not self.fut.done():
            self.fut.set_exception(exc)
            self.transport.pause_reading()

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        spawn = self.expecter.spawn
        s = spawn._decoder.decode(data)
        spawn._log(s, "read")

        if self.fut.done():
            spawn._before.write(s)
            spawn._buffer.write(s)
            return

        try:
            index = self.expecter.new_data(s)
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
            self.expecter.spawn.has_eof = True
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
