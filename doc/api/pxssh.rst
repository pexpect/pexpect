pxssh - control an SSH session
==============================

.. note::

   *pxssh* is a screen-scraping wrapper around the SSH command on your system.
   In many cases, you should consider using
   `Paramiko <https://github.com/paramiko/paramiko>`_ or
   `RedExpect <https://github.com/Red-M/RedExpect>`_ instead.
   Paramiko is a Python module which speaks the SSH protocol directly, so it
   doesn't have the extra complexity of running a local subprocess.
   RedExpect is very similar to pxssh except that it reads and writes directly
   into an SSH session all done via Python with all the SSH protocol in C,
   additionally it is written for communicating to SSH servers that are not just
   Linux machines. Meaning that it is extremely fast in comparison to Paramiko
   and already has the familiar expect API. In most cases RedExpect and pxssh
   code should be fairly interchangeable.

.. automodule:: pexpect.pxssh

.. autoclass:: ExceptionPxssh

pxssh class
-----------

.. autoclass:: pxssh

   .. automethod:: __init__

   .. attribute:: PROMPT

      The regex pattern to search for to find the prompt. If you call :meth:`login`
      with ``auto_prompt_reset=False``, you must set this attribute manually.

   .. attribute:: force_password

      If this is set to ``True``, public key authentication is disabled, forcing the
      server to ask for a password. Note that the sysadmin can disable password
      logins, in which case this won't work.

   .. attribute:: options

      The dictionary of user specified SSH options, eg, ``options = dict(StrictHostKeyChecking="no", UserKnownHostsFile="/dev/null")``

   .. automethod:: login
   .. automethod:: logout
   .. automethod:: prompt
   .. automethod:: sync_original_prompt
   .. automethod:: set_unique_prompt
