#!/usr/bin/env python
# This program is completely unaware of encodings, it just writes raw bytes,
# which happens to be utf-8 for ascending ansi-art-like blocks. However, only
# a single byte of multibyte utf-8 sequences are yielded each fraction of a
# second, testing Issue #9, which will yield a UnicodeDecodeError for
# incompletely decoded bytes, even though it looks fine in say, a Terminal
# (unless you interrupt the output bytes by holding down the spacebar!)
import sys, time
utf8_blurb = (b'\xe2', b'\x96', b'\x81',
              b'\xe2', b'\x96', b'\x82',
              b'\xe2', b'\x96', b'\x83',
              b'\xe2', b'\x96', b'\x84',
              b'\xe2', b'\x96', b'\x85',
              b'\xe2', b'\x96', b'\x86',
              b'\xe2', b'\x96', b'\x87',
              b'\xe2', b'\x96', b'\x88',)
import os
for ch in utf8_blurb:
    os.write(sys.stderr.fileno(), ch)
    time.sleep(0.05)
    sys.stderr.flush()
sys.stderr.write('\n')
