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


@unittest.skipIf(asyncio is None, "Requires asyncio")
class AsyncTests(PexpectTestCase.AsyncPexpectTestCase):
    async def test_simple_expect(self):
        p = pexpect.spawn("cat")
        p.sendline("Hello asyncio")
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
        p.sendline("Hi")
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
