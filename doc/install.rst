Installation
============

Pexpected is on PyPI, and can be installed with standard tools::

    pip install pexpected

Or::

    easy_install pexpected

Note that the name is 'pexpected' for installation, but 'pexpect' for imports.

Requirements
------------

Pexpected requires Python 2.6 or 3.2 or above. For older versions of Python,
continue using Pexpect.

Pexpected (and Pexpect) only work on POSIX systems, where the :mod:`pty` module
is present in the standard library. It may be possible to run it on Windows
using `Cygwin <http://www.cygwin.com/>`_.