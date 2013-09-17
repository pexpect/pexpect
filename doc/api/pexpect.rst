pexpect module
==============

.. automodule:: pexpect

spawn object
------------

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

run function
------------

.. autofunction:: run

Exceptions
----------

.. autoclass:: EOF

.. autoclass:: TIMEOUT

.. autoclass:: ExceptionPexpect

Utility functions
-----------------

.. autofunction:: which

.. autofunction:: split_command_line