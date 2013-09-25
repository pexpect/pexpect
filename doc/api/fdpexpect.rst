fdpexpect - use pexpect with a file descriptor
==============================================

.. automodule:: pexpect.fdpexpect

fdspawn class
-------------

.. autoclass:: fdspawn
   :show-inheritance:

   .. automethod:: __init__
   .. automethod:: isalive
   .. automethod:: close

   .. note::
      :class:`fdspawn` inherits all of the methods of :class:`~pexpect.spawn`, 
      but not all of them can be used, especially if the file descriptor is not
      a terminal. Some methods may do nothing (e.g. :meth:`~fdspawn.kill`), while
      others will raise an exception (e.g. :meth:`~fdspawn.terminate`).
      This behaviour might be made more consistent in the future, so try to
      avoid relying on it.