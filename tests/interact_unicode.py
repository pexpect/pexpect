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

import pexpect
import sys

def main():
    p = pexpect.spawnu(sys.executable + ' echo_w_prompt.py')
    p.interact()

if __name__ == '__main__':
    main()
