try:
    import asyncio
except ImportError:
    asyncio = None

import sys
import unittest

import pexpect
from .PexpectTestCase import PexpectTestCase

def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

@unittest.skipIf(asyncio is None, "Requires asyncio")
class AsyncTests(PexpectTestCase):
    def test_simple_expect(self):
        p = pexpect.spawn('cat')
        p.sendline('Hello asyncio')
        coro = p.expect(['Hello', pexpect.EOF] , async=True)
        assert run(coro) == 0
        print('Done')

    def test_timeout(self):
        p = pexpect.spawn('cat')
        coro = p.expect('foo', timeout=1, async=True)
        with self.assertRaises(pexpect.TIMEOUT):
            run(coro)
        
        p = pexpect.spawn('cat')
        coro = p.expect(['foo', pexpect.TIMEOUT], timeout=1, async=True)
        assert run(coro) == 1

    def test_eof(self):
        p = pexpect.spawn('cat')
        p.sendline('Hi')
        coro = p.expect(pexpect.EOF, async=True)
        p.sendeof()
        assert run(coro) == 0

        p = pexpect.spawn('cat')
        p.sendeof()
        coro = p.expect('Blah', async=True)
        with self.assertRaises(pexpect.EOF):
            run(coro)
    
    def test_expect_exact(self):
        p = pexpect.spawn('%s list100.py' % sys.executable)
        assert run(p.expect_exact(b'5', async=True)) == 0
        assert run(p.expect_exact(['wpeok', b'11'], async=True)) == 1
        assert run(p.expect_exact([b'foo', pexpect.EOF], async=True)) == 1
