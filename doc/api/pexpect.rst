Core pexpect components
=======================

.. automodule:: pexpect

spawn class
-----------

.. autoclass:: spawn

   .. automethod:: __init__
   .. automethod:: expect
   .. automethod:: expect_exact
   .. automethod:: expect_list
   .. automethod:: compile_pattern_list
   .. automethod:: send
   .. automethod:: sendline
   .. automethod:: write
   .. automethod:: writelines
   .. automethod:: sendcontrol
   .. automethod:: sendeof
   .. automethod:: sendintr
   .. automethod:: read
   .. automethod:: readline
   .. automethod:: read_nonblocking
   .. automethod:: eof
   .. automethod:: interact

   .. attribute:: logfile
                  logfile_read
                  logfile_send

      Set these to a Python file object (or :data:`sys.stdout`) to log all
      communication, data read from the child process, or data sent to the child
      process.

      .. note::

         With a :class:`spawn` instance, the log files should be open for
         writing binary data. With a :class:`spawnu` instance, they should
         be open for writing unicode text.

Controlling the child process
`````````````````````````````

.. class:: spawn

   .. automethod:: kill
   .. automethod:: terminate
   .. automethod:: isalive
   .. automethod:: wait
   .. automethod:: close
   .. automethod:: getwinsize
   .. automethod:: setwinsize
   .. automethod:: getecho
   .. automethod:: setecho
   .. automethod:: waitnoecho

   .. attribute:: pid

      The process ID of the child process.

   .. attribute:: child_fd

      The file descriptor used to communicate with the child process.

.. _unicode:

Handling unicode
````````````````

For backwards compatibility, :class:`spawn` can handle some Unicode: its
send methods will encode arbitrary unicode as UTF-8 before sending it to the
child process, and its expect methods can accept ascii-only unicode strings.
However, for a proper unicode API to a subprocess, use this subclass:

.. autoclass:: spawnu
   :show-inheritance:

There is also a :func:`runu` function, the unicode counterpart to :func:`run`.

.. note::

   Unicode handling with pexpect works the same way on Python 2 and 3, despite
   the difference in names. I.e.:

   - :class:`spawn` works with ``str`` on Python 2, and :class:`bytes` on Python 3,
   - :class:`spawnu` works with ``unicode`` on Python 2, and :class:`str` on Python 3.

run function
------------

.. autofunction:: run

.. autofunction:: runu

Exceptions
----------

.. autoclass:: EOF

.. autoclass:: TIMEOUT

.. autoclass:: ExceptionPexpect

Utility functions
-----------------

.. autofunction:: which

.. autofunction:: split_command_line
