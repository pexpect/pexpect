#!/usr/bin/env python
'''
Just like interact.py, but using spawnu instead of spawn
'''
try:
    # This allows coverage to measure code run in this process
    import coverage
    coverage.process_startup()
except ImportError:
    pass

from utils import no_coverage_env
import pexpect
import codecs
import sys

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)


def main():
    p = pexpect.spawnu(sys.executable + ' echo_w_prompt.py',
                       env=no_coverage_env())
    p.interact()
    print("Escaped interact")

if __name__ == '__main__':
    main()
