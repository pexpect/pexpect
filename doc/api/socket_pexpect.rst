socket_pexpect - use pexpect with a socket
==========================================

.. automodule:: pexpect.socket_pexpect

Working with an existing connection
-----------------------------------

:class:`SocketSpawn` wraps an already connected :class:`socket.socket`; it
does not start a child process or open the connection for you. Unlike
:class:`pexpect.fdpexpect.fdspawn`, it uses the socket API rather than
``os.read`` and ``os.write``, so it can be used on Windows as well as Unix.

For a network service, open the connection with
:func:`socket.create_connection` and pass the resulting socket to
:class:`SocketSpawn`. This self-contained example uses a connected socket pair
to demonstrate sending data and matching the peer's response without an
external server::

    import socket
    from pexpect.socket_pexpect import SocketSpawn

    client, peer = socket.socketpair()
    try:
        session = SocketSpawn(client, timeout=5)
        session.send(b"status\n")
        assert peer.recv(1024) == b"status\n"
        peer.sendall(b"READY\r\n")
        session.expect_exact(b"READY\r\n")
        assert session.after == b"READY\r\n"
    finally:
        client.close()
        peer.close()

Use byte strings for patterns and data with the default ``encoding=None``.
Socket input is not passed through a terminal, so line endings are those sent
by the peer, without the terminal's newline translation. Close the connection
when finished: :meth:`SocketSpawn.close` shuts down and closes the wrapped
socket, or you can close the original socket yourself as above.

SocketSpawn class
-----------------

.. autoclass:: SocketSpawn
   :show-inheritance:

   .. automethod:: __init__
   .. automethod:: isalive
   .. automethod:: close

   .. method:: expect
               expect_exact
               expect_list

      As :class:`pexpect.spawn`.
