.. image:: https://travis-ci.org/pexpect/pexpect.png?branch=master
   :target: https://travis-ci.org/pexpect/pexpect
   :align: right
   :alt: Build status

Pexpect is a Pure Python Expect-like module

Pexpect makes Python a better tool for controlling other applications.

Pexpect is a pure Python module for spawning child applications; controlling
them; and responding to expected patterns in their output. Pexpect works like
Don Libes' Expect. Pexpect allows your script to spawn a child application and
control it as if a human were typing commands.

Pexpect can be used for automating interactive applications such as ssh, ftp,
passwd, telnet, etc. It can be used to a automate setup scripts for duplicating
software package installations on different servers. It can be used for
automated software testing. Pexpect is in the spirit of Don Libes' Expect, but
Pexpect is pure Python. Unlike other Expect-like modules for Python, Pexpect
does not require TCL or Expect nor does it require C extensions to be compiled.
It should work on any platform that supports the standard Python pty module.
The Pexpect interface was designed to be easy to use.

If you want to work with the development version of the source code then please
read the DEVELOPERS.rst document in the root of the source code tree.

Free, open source, and all that good stuff.

You can install Pexpect using pip::

    pip install pexpect

`Docs on ReadTheDocs <http://pexpect.readthedocs.org/>`_

PEXPECT LICENSE

.. code-block:: text

    http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2012-2014, Noah Spurrier <noah@noah.org>

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

This license is approved by the OSI and FSF as GPL-compatible.
