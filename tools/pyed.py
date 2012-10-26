"""This represents a document with methods to allow easy editing.
Think 'sed', only more fun to use.
Example 1: Convert all python-style comments in a file to UPPERCASE.
This operates as a filter on stdin, so this needs a shell pipe.
cat myscript.py | upper_filter.py
    import sys, pyed
    pe = pyed()
    pe.read(sys.stdin)
    for pe in pe.match_lines('^\\s*#'):
        pe.cur_line = pe.cur_line.upper()
    print pe

Example 2: Edit an Apache2 httpd.conf file to turn on supplemental SSL configuration.
    import pyed
    pe = pyed()
    pe.read("httpd.conf")
    pe.first('#Include conf/extra/httpd-ssl.conf')
    pe.cur_line = 'Include conf/extra/httpd-ssl.conf'
    pe.write("httpd.conf")

PEXPECT LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2012, Noah Spurrier <noah@noah.org>
    PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
    PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
    COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""

import re
class pyed (object):
    def __init__ (self, new_str=None):
        if new_str is not None:
            self.lines = new_str.splitlines()
            self.cur_line_num = 0
        else:
            self.lines = None
            # force invalid line number
            self.cur_line_num = None
    def match_lines (self, pattern, beg=0, end=None):
        """This returns a generator that iterates this object
        over the lines and yielding when a line matches the pattern.
        Note that this generator mutates this object so that
        the cur_line is changed to the line matching the pattern.
        """
        p = re.compile (pattern)
        if end is None:
            end = len(self.lines)
        for i in xrange (beg,end):
            m = p.match(self.lines[i])
            if m is not None:
                self.cur_line_num = i
                yield self
            else:
                # force invalid line number
                cur_line_num = None
    def match_lines_rev (self, pattern, beg=0, end=None):
        """This is similar to match_lines, but the order is reversed.
        """
        p = re.compile (pattern)
        if end is None:
            end = len(self.lines)
        for i in xrange (end-1,beg-1,-1):
            m = p.match(self.lines[i])
            if m is not None:
                self.cur_line_num = i
                yield self
            else:
                # force invalid line number
                cur_line_num = None
    def next (self):
        self.cur_line_num = self.cur_line_num + 1
        if self.cur_line_num >= len(self.lines):
            self.cur_line_num = len(self.lines) - 1
        return self.cur_line
    def prev (self):
        self.cur_line_num = self.cur_line_num - 1
        if self.cur_line_num < 0:
            self.cur_line_num = 0
        return self.cur_line
    def first (self, pattern=None):
        if pattern is not None:
            try:
                return self.match_lines(pattern).next()
            except StopIteration, e:
                # force invalid line number
                self.cur_line_num = None
                return None
        self.cur_line_num = 0
        return self.cur_line
    def last (self, pattern=None):
        if pattern is not None:
            try:
                return self.match_lines_rev(pattern).next()
            except StopIteration, e:
                # force invalid line number
                self.cur_line_num = None
                return None
        self.cur_line_num = len(self.lines) - 1
        return self.cur_line
    def insert (self, s=''):
        """This inserts the string as a new line before the current line number.
        """
        self.lines.insert(self.cur_line_num, s)
    def append (self, s=''):
        """Unlike list append, this appends after the current line number,
        not at the end of the entire list.
        """
        self.cur_line_num = self.cur_line_num + 1
        self.lines.insert(self.cur_line_num, s)
    def delete (self):
        del self.cur_line
    def read (self, file_holder):
        """This reads all the lines from a file. The file_holder may be
        either a string filename or any object that supports "read()".
        All previous lines are lost.
        """
        if hasattr(file_holder, 'read') and callable(file_holder.read):
            fin = file_holder
        else:
            fin = open (file_holder, 'rb')
        data = fin.read()
        self.lines = data.splitlines()
        self.cur_line_num = 0
    def write (self, file_holder):
        """This writes all the lines to a file. The file_holder may be
        either a string filename or any object that supports "read()".
        TODO: Make write be atomic using file move instead of overwrite.
        """
        if hasattr(file_holder, 'write') and callable(file_holder.write):
            fout = file_holder
        else:
            fout = open (file_holder, 'wb')
        for l in self.lines:
            fout.write(l)
            fout.write('\n')
    # the following are for smart properties.
    def __str__ (self):
        return '\n'.join(self.lines)
    def __get_cur_line (self):
        self.__cur_line = self.lines[self.cur_line_num]
        return self.__cur_line
    def __set_cur_line (self, value):
        self.__cur_line = value
        self.lines[self.cur_line_num] = self.__cur_line
    def __del_cur_line (self):
        del self.lines[self.cur_line_num]
        if self.cur_line_num >= len(self.lines):
            self.cur_line_num = len(self.lines) - 1
    cur_line = property (__get_cur_line, __set_cur_line, __del_cur_line)
    # lines = property (get_lines, set_lines, del_lines)

__NOT_USED ="""
import sys
pe = pyed()
pe.read(sys.stdin)
#print "---"
#print list(x.cur_line for x in pe.match_lines_rev('^#'))
#print pe.first('^#')
#print pe.last('^#')
#print "---"
for pe in pe.match_lines('^\\s*#'):
    pe.cur_line = pe.cur_line.lower()
pe.last('# comment.*')
pe.cur_line = '# Comment 1'
print pe
if pe.last('asdfasdf') is None:
    print "can't find 'asdfasdf'"
"""

