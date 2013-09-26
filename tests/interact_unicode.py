#!/usr/bin/env python
'''
Just like interact.py, but using spawnu instead of spawn
'''
import pexpect
import sys

def main():
    p = pexpect.spawnu(sys.executable + ' echo_w_prompt.py')
    p.interact()

if __name__ == '__main__':
    main()
