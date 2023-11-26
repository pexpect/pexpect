import sys


if sys.version_info < (3, 5):
    collect_ignore = (
        'test_async.py',
    )

if sys.version_info[0] == 2:
    import unittest
    setattr(
        unittest.TestCase,
        'assertRaisesRegex',
        unittest.TestCase.assertRaisesRegexp,
    )
