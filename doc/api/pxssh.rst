pxssh module
============

.. automodule:: pexpect.pxssh

.. autoclass:: ExceptionPxssh

pxssh class
-----------

.. autoclass:: pxssh

   .. automethod:: __init__

   .. attribute:: auto_prompt_reset

      Set this to False to prevent :meth:`login` from setting a unique prompt
      which can easily be located.

   .. attribute:: PROMPT

      The regex pattern to search for to find the prompt. If
      :attr:`auto_prompt_reset` is False, you must set this attribute manually.

   .. automethod:: login
   .. automethod:: logout
   .. automethod:: prompt
   .. automethod:: sync_original_prompt
   .. automethod:: set_unique_prompt