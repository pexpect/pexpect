try:
    import asyncio
    loop = asyncio.get_event_loop()
except ImportError:
    asyncio = None

import pexpect
import unittest

@unittest.skipIf(asyncio is None, "Requires asyncio")
class AsyncTests(unittest.TestCase):
    def test_simple_expect(self):
        p = pexpect.spawn('cat')
        p.sendline('Hello asyncio')
        coro = p.expect('Hello', async=True)
        task = asyncio.Task(coro)
        results = []
        def complete(task):
            results.append(task.result())
        task.add_done_callback(complete)
        loop.run_until_complete(task)
        
        assert results == [0]