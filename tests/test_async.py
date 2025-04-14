try:
    import asyncio
except ImportError:
    asyncio = None

import gc
import sys
import unittest

import pexpect
from pexpect import replwrap

from . import PexpectTestCase

_CAT_EOF = b'^D\x08\x08'

@unittest.skipIf(asyncio is None, "Requires asyncio")
class AsyncTests(PexpectTestCase.AsyncPexpectTestCase):
    async def test_simple_expect(self):
        p = pexpect.spawn("cat")
        await p.sendline("Hello asyncio", async_=True)
        assert await p.expect(["Hello", pexpect.EOF], async_=True) == 0
        print("Done")

    async def test_timeout(self):
        p = pexpect.spawn("cat")
        with self.assertRaises(pexpect.TIMEOUT):
            await p.expect("foo", timeout=1, async_=True)

        p = pexpect.spawn("cat")
        assert await p.expect(["foo", pexpect.TIMEOUT], timeout=1, async_=True) == 1

    async def test_eof(self):
        p = pexpect.spawn("cat")
        await p.sendline("Hi", async_=True)
        p.sendeof()
        assert await p.expect(pexpect.EOF, async_=True) == 0

        p = pexpect.spawn("cat")
        p.sendeof()
        with self.assertRaises(pexpect.EOF):
            await p.expect("Blah", async_=True)

    async def test_expect_exact(self):
        p = pexpect.spawn("%s list100.py" % self.PYTHONBIN)
        assert await p.expect_exact(b"5", async_=True) == 0
        assert await p.expect_exact(["wpeok", b"11"], async_=True) == 1
        assert await p.expect_exact([b"foo", pexpect.EOF], async_=True) == 1

    async def test_async_utf8(self):
        p = pexpect.spawn("%s list100.py" % self.PYTHONBIN, encoding="utf8")
        assert await p.expect_exact("5", async_=True) == 0
        assert await p.expect_exact(["wpeok", "11"], async_=True) == 1
        assert await p.expect_exact(["foo", pexpect.EOF], async_=True) == 1

    async def test_async_and_gc(self):
        p = pexpect.spawn("%s sleep_for.py 1" % self.PYTHONBIN, encoding="utf8")
        assert await p.expect_exact("READY", async_=True) == 0
        gc.collect()
        assert await p.expect_exact("END", async_=True) == 0

    async def test_async_and_sync(self):
        p = pexpect.spawn("echo 1234", encoding="utf8", maxread=1)
        assert await p.expect_exact("1", async_=True) == 0
        assert p.expect_exact("2") == 0
        assert await p.expect_exact("3", async_=True) == 0

    async def test_async_replwrap(self):
        bash = replwrap.bash()
        res = await bash.run_command("time", async_=True)
        assert "real" in res, res

    async def test_async_replwrap_multiline(self):
        bash = replwrap.bash()
        res = await bash.run_command("echo '1 2\n3 4'", async_=True)
        self.assertEqual(res.strip().splitlines(), ["1 2", "3 4"])

        # Should raise ValueError if input is incomplete
        try:
            await bash.run_command("echo '5 6", async_=True)
        except ValueError:
            pass
        else:
            assert False, "Didn't raise ValueError for incomplete input"

        # Check that the REPL was reset (SIGINT) after the incomplete input
        res = await bash.run_command("echo '1 2\n3 4'", async_=True)
        self.assertEqual(res.strip().splitlines(), ["1 2", "3 4"])

    async def test_terminate_async(self):
        " test force terminate always succeeds (SIGKILL) in async mode. "
        child = pexpect.spawn('cat')
        await child.terminate(force=1, async_=True)
        await child.terminate(force=1, async_=True)
        assert child.terminated

    async def test_waitnoecho_async(self):
        " Tests setecho(False) followed by waitnoecho() "
        p = pexpect.spawn('cat', echo=False, timeout=5)
        try:
            p.setecho(False)
            await p.waitnoecho(async_=True)
        except IOError:
            if sys.platform.lower().startswith('sunos'):
                if hasattr(unittest, 'SkipTest'):
                    raise unittest.SkipTest("Not supported on this platform.")
                return 'skip'
            raise

    async def test_readline_async(self):
        " Test spawn.readline(). "
        # when argument 0 is sent, nothing is returned.
        # Otherwise the argument value is meaningless.
        child = pexpect.spawn('cat', echo=False)
        await child.sendline("alpha", async_=True)
        await child.sendline("beta", async_=True)
        await child.sendline("gamma", async_=True)
        await child.sendline("delta", async_=True)
        child.sendeof()
        assert await child.readline(0, async_=True) == b''
        assert (await child.readline(async_=True)).rstrip() == b'alpha'
        assert (await child.readline(1, async_=True)).rstrip() == b'beta'
        assert (await child.readline(2, async_=True)).rstrip() == b'gamma'
        assert (await child.readline(async_=True)).rstrip() == b'delta'
        await child.expect(pexpect.EOF, async_=True)
        assert not child.isalive()
        assert child.exitstatus == 0

#    async def test_iter_async(self):
#        " iterating over lines of spawn.__iter__(). "
#        child = pexpect.spawn('cat', echo=False)
#        child.sendline("abc")
#        child.sendline("123")
#        child.sendeof()
#        # Don't use ''.join() because we want to test __iter__().
#        page = b''
#        for line in child:
#            page += line
#        page = page.replace(_CAT_EOF, b'')
#        assert page == b'abc\r\n123\r\n'

    async def test_readlines_async(self):
        " reading all lines of spawn.readlines(). "
        child = pexpect.spawn('cat', echo=False)
        await child.sendline("abc", async_=True)
        await child.sendline("123", async_=True)
        child.sendeof()
        page = b''.join(await child.readlines(async_=True)).replace(_CAT_EOF, b'')
        assert page == b'abc\r\n123\r\n'
        await child.expect(pexpect.EOF, async_=True)
        assert not child.isalive()
        assert child.exitstatus == 0

    async def test_write_async(self):
        " write a character and return it in return. "
        child = pexpect.spawn('cat', echo=False)
        await child.write('a', async_=True)
        await child.write('\r', async_=True)
        self.assertEqual(await child.readline(async_=True), b'a\r\n')

    async def test_writelines_async(self):
        " spawn.writelines() "
        child = pexpect.spawn('cat')
        # notice that much like file.writelines, we do not delimit by newline
        # -- it is equivalent to calling write(''.join([args,]))
        await child.writelines(['abc', '123', 'xyz', '\r'], async_=True)
        child.sendeof()
        line = await child.readline(async_=True)
        assert line == b'abc123xyz\r\n'
