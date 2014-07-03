try:
    import asyncio
except ImportError:
    asyncio = None

import pexpect
import unittest

def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

@unittest.skipIf(asyncio is None, "Requires asyncio")
class AsyncTests(unittest.TestCase):
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