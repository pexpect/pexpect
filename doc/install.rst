Installation
============

Pexpect is on PyPI, and can be installed with standard tools::

    pip install pexpect

Or::

    easy_install pexpect

Requirements
------------

This version of Pexpect requires Python 2.6 or 3.2 or above. For older
versions of Python, continue using Pexpect 2.4.

As of version 4.0, Pexpect can be used on Windows and POSIX systems. However,
:class:`pexpect.spawn` and :func:`pexpect.run` are only available on POSIX,
where the :mod:`pty` module is present in the standard library. See
:ref:`windows` for more information.
