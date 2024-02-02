"""Implementation of coroutines using ``async def``/``await`` keywords.

These keywords replaced ``@asyncio.coroutine`` and ``yield from`` from
Python 3.5 onwards.
"""
import asyncio
import errno
import signal
from sys import version_info as py_version_info
import os

from pexpect import EOF

if py_version_info >= (3, 7):
    # get_running_loop, new in 3.7, is preferred to get_event_loop
    _loop_getter = asyncio.get_running_loop
else:
    # Deprecation warning since 3.10
    _loop_getter = asyncio.get_event_loop


async def expect_async(expecter, timeout=None):
    # First process data that was previously read - if it maches, we don't need
    # async stuff.
    idx = expecter.existing_data()
    if idx is not None:
        return idx

    if expecter.spawn.has_eof:
        return expecter.eof()

    if not expecter.spawn.async_pw_transport:
        pattern_waiter = PatternWaiter()
        pattern_waiter.set_expecter(expecter)
        transport, pattern_waiter = await _loop_getter().connect_read_pipe(
            lambda: pattern_waiter, expecter.spawn
        )
        expecter.spawn.async_pw_transport = pattern_waiter, transport
    else:
        pattern_waiter, transport = expecter.spawn.async_pw_transport
        pattern_waiter.set_expecter(expecter)
        transport.resume_reading()
    try:
        return (await asyncio.wait_for(pattern_waiter.fut, timeout))
    except asyncio.TimeoutError as exc:
        transport.pause_reading()
        return expecter.timeout(exc)


async def repl_run_command_async(repl, command, cmdlines, timeout=-1):
    res = []
    await repl.child.sendline(cmdlines[0], async_=True)
    for line in cmdlines[1:]:
        await repl._expect_prompt(timeout=timeout, async_=True)
        res.append(repl.child.before)
        await repl.child.sendline(line, async_=True)

    # Command was fully submitted, now wait for the next prompt
    prompt_idx = await repl._expect_prompt(timeout=timeout, async_=True)
    if prompt_idx == 1:
        # We got the continuation prompt - command was incomplete
        repl.child.kill(signal.SIGINT)
        await repl._expect_prompt(timeout=1, async_=True)
        raise ValueError("Continuation prompt found - input was incomplete\n"
                             + command)
    return "".join(res + [repl.child.before])

async def spawn__waitnoecho_async(spawn, timeout, end_time):
    while True:
        if not spawn.getecho():
            return True
        if timeout < 0 and timeout is not None:
            return False
        if timeout is not None:
            timeout = end_time - time.time()
        await asyncio.sleep(0.1)

async def spawn__write_async(spawn, s):
    await spawn.send(s, async_=True)

async def spawn__writelines_async(spawn, sequence):
    for s in sequence:
        await spawn.write(s, async_=True)

async def spawn__send_async(spawn, s):
    if spawn.delaybeforesend is not None:
        await asyncio.sleep(spawn.delaybeforesend)

    s = spawn._coerce_send_string(s)
    spawn._log(s, 'send')

    b = spawn._encoder.encode(s, final=False)
    return os.write(spawn.child_fd, b)

async def spawn__terminate_async(spawn, force=False):
    if not spawn.isalive():
        return True

    try:
        spawn.kill(signal.SIGHUP)
        await asyncio.sleep(spawn.delayafterterminate)
        if not spawn.isalive():
            return True
        spawn.kill(signal.SIGCONT)
        await asyncio.sleep(spawn.delayafterterminate)
        if not spawn.isalive():
            return True
        spawn.kill(signal.SIGINT)
        await asyncio.sleep(spawn.delayafterterminate)
        if not spawn.isalive():
            return True
        if force:
            spawn.kill(signal.SIGKILL)
            await asyncio.sleep(spawn.delayafterterminate)
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
        await asyncio.sleep(spawn.delayafterterminate)
        if not spawn.isalive():
            return True
        else:
            return False

async def spawnbase__read_async(spawn, size):

    if size == 0:
        return spawn.string_type()
    if size < 0:
        # delimiter default is EOF
        await spawn.expect(spawn.delimiter, async_=True)
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
    index = await spawn.expect([cre, spawn.delimiter], async_=True)
    if index == 0:
        ### FIXME spawn.before should be ''. Should I assert this?
        return spawn.after
    return spawn.before

async def spawnbase__readline_async(spawn, size):
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
    index = await spawn.expect([spawn.crlf, spawn.delimiter], async_=True)
    if index == 0:
        return spawn.before + spawn.crlf
    else:
        return spawn.before

async def spawnbase__readlines_async(spawn, sizehint):
    '''This reads until EOF using readline() and returns a list containing
    the lines thus read. The optional 'sizehint' argument is ignored.
    Remember, because this reads until EOF that means the child
    process should have closed its stdout. If you run this method on
    a child that is still running with its stdout open then this
    method will block until it timesout.'''

    lines = []
    while True:
        line = await spawn.readline(async_=True)
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
        except Exception as exc:
            self.expecter.errored()
            self.error(exc)

    def eof_received(self):
        # N.B. If this gets called, async will close the pipe (the spawn object)
        # for us
        try:
            self.expecter.spawn.flag_eof = True
            self.expecter.spawn.has_eof = True
            index = self.expecter.eof()
        except EOF as exc:
            self.error(exc)
        else:
            self.found(index)

    def connection_lost(self, exc):
        if isinstance(exc, OSError) and exc.errno == errno.EIO:
            # We may get here without eof_received being called, e.g on Linux
            self.eof_received()
        elif exc is not None:
            self.error(exc)
