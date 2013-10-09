#!/usr/bin/env python
# This program is completely unaware of encodings, it just writes raw bytes,
# which happens to be utf-8 for ascending ansi-art-like blocks. However, only
# a single byte of multibyte utf-8 sequences are yielded each fraction of a
# second, testing Issue #9, which will yield a UnicodeDecodeError for
# incompletely decoded bytes, even though it looks fine in say, a Terminal
# (unless you interrupt the output bytes by holding down the spacebar!)
import sys, time
utf8_blurb = ('\xe2\x96\x81\xe2\x96\x82\xe2\x96\x83\xe2\x96\x84'
              '\xe2\x96\x85\xe2\x96\x86\xe2\x96\x87\xe2\x96\x88')
for ch in utf8_blurb:
    sys.stderr.write(ch)
    sys.stderr.flush()
    time.sleep(0.05)
sys.stderr.write('\n')
