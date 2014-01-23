pxssh - control an SSH session
==============================

.. automodule:: pexpect.pxssh

.. autoclass:: ExceptionPxssh

pxssh class
-----------

.. autoclass:: pxssh

   .. automethod:: __init__

   .. attribute:: PROMPT

      The regex pattern to search for to find the prompt. If you call :meth:`login`
      with ``auto_prompt_reset=False``, you must set this attribute manually.

   .. automethod:: login
   .. automethod:: logout
   .. automethod:: prompt
   .. automethod:: sync_original_prompt
   .. automethod:: set_unique_prompt
