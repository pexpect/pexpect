History
=======

Releases
--------

Version 3.3
```````````

* Fix various issues related to SunOS (SmartOS).  A new keyword argument has
  been included, ``echo=True`` by default, for the ``spawn()`` constructor.
  On SRV4 systems, the master process may not use ``setecho()``, ``getecho()``,
  ``getwinsize()``, ``setwinsize()`` or ``waitnoecho()``, because the master_fd
  side of the pty-pair does not appear as a terminal (``isatty()`` returns
  False) (:ghissue:`44`).
* Fixed issue where pexpect would attempt to execute a directory because
  it has the 'execute' bit set (:ghissue:`37`).

Version 3.2
```````````

* Fix exception handling from :func:`select.select` on Python 2 (:ghpull:`38`).
  This was accidentally broken in the previous release when it was fixed for
  Python 3.
* Removed a workaround for ``TIOCSWINSZ`` on very old systems, which was causing
  issues on some BSD systems (:ghpull:`40`).
* Fixed an issue with exception handling in :mod:`~pexpect.pxssh` (:ghpull:`43`)

The documentation for :mod:`~pexpect.pxssh` was improved.

Version 3.1
```````````

* Fix an issue that prevented importing pexpect on Python 3 when ``sys.stdout``
  was reassigned (:ghissue:`30`).
* Improve prompt synchronisation in :mod:`~pexpect.pxssh` (:ghpull:`28`).
* Fix pickling exception instances (:ghpull:`34`).
* Fix handling exceptions from :func:`select.select` on Python 3 (:ghpull:`33`).

The examples have also been cleaned up somewhat - this will continue in future
releases.

Version 3.0
```````````

The new major version number doesn't indicate any deliberate API incompatibility.
We have endeavoured to avoid breaking existing APIs. However, pexpect is under
new maintenance after a long dormancy, so some caution is warranted.

* A new :ref:`unicode API <unicode>` was introduced.
* Python 3 is now supported, using a single codebase.
* Pexpect now requires at least Python 2.6 or 3.2.
* The modules other than pexpect, such as :mod:`pexpect.fdpexpect` and
  :mod:`pexpect.pxssh`, were moved into the pexpect package. For now, wrapper
  modules are installed to the old locations for backwards compatibility (e.g.
  ``import pxssh`` will still work), but these will be removed at some point in
  the future.
* Ignoring ``SIGHUP`` is now optional - thanks to Kimmo Parviainen-Jalanko for
  the patch.

We also now have `docs on ReadTheDocs <http://pexpect.readthedocs.org/>`_,
and `continuous integration on Travis CI <https://travis-ci.org/pexpect/pexpect>`_.

Version 2.4
```````````

* Fix a bug regarding making the pty the controlling terminal when the process
  spawning it is not, actually, a terminal (such as from cron)

Version 2.3
```````````

* Fixed OSError exception when a pexpect object is cleaned up. Previously, you
  might have seen this exception::

      Exception exceptions.OSError: (10, 'No child processes')
      in <bound method spawn.__del__ of <pexpect.spawn instance at 0xd248c>> ignored

  You should not see that anymore. Thanks to Michael Surette.
* Added support for buffering reads. This greatly improves speed when trying to
  match long output from a child process. When you create an instance of the spawn
  object you can then set a buffer size. For now you MUST do the following to turn
  on buffering -- it may be on by default in future version::

      child = pexpect.spawn ('my_command')
      child.maxread=1000 # Sets buffer to 1000 characters.

* I made a subtle change to the way TIMEOUT and EOF exceptions behave.
  Previously you could either expect these states in which case pexpect
  will not raise an exception, or you could just let pexpect raise an
  exception when these states were encountered. If you expected the
  states then the ``before`` property was set to everything before the
  state was encountered, but if you let pexpect raise the exception then
  ``before`` was not set. Now, the ``before`` property will get set either
  way you choose to handle these states.
* The spawn object now provides iterators for a *file-like interface*.
  This makes Pexpect a more complete file-like object. You can now write
  code like this::

      child = pexpect.spawn ('ls -l')
      for line in child:
          print line

* write and writelines() no longer return a value. Use send() if you need that
  functionality. I did this to make the Spawn object more closely match a
  file-like object.
* Added the attribute ``exitstatus``. This will give the exit code returned
  by the child process. This will be set to ``None`` while the child is still
  alive. When ``isalive()`` returns 0 then ``exitstatus`` will be set.
* Made a few more tweaks to ``isalive()`` so that it will operate more
  consistently on different platforms. Solaris is the most difficult to support.
* You can now put ``TIMEOUT`` in a list of expected patterns. This is just like
  putting ``EOF`` in the pattern list. Expecting for a ``TIMEOUT`` may not be
  used as often as ``EOF``, but this makes Pexpect more consitent.
* Thanks to a suggestion and sample code from Chad J. Schroeder I added the ability
  for Pexpect to operate on a file descriptor that is already open. This means that
  Pexpect can be used to control streams such as those from serial port devices. Now,
  you just pass the integer file descriptor as the "command" when constructing a
  spawn open. For example on a Linux box with a modem on ttyS1::

      fd = os.open("/dev/ttyS1", os.O_RDWR|os.O_NONBLOCK|os.O_NOCTTY)
      m = pexpect.spawn(fd) # Note integer fd is used instead of usual string.
      m.send("+++") # Escape sequence
      m.send("ATZ0\r") # Reset modem to profile 0
      rval = m.expect(["OK", "ERROR"])

* ``read()`` was renamed to ``read_nonblocking()``. Added new ``read()`` method
  that matches file-like object interface. In general, you should not notice
  the difference except that ``read()`` no longer allows you to directly set the
  timeout value. I hope this will not effect any existing code. Switching to
  ``read_nonblocking()`` should fix existing code.
* Changed the name of ``set_echo()`` to ``setecho()``.
* Changed the name of ``send_eof()`` to ``sendeof()``.
* Modified ``kill()`` so that it checks to make sure the pid ``isalive()``.
* modified ``spawn()`` (really called from ``__spawn()``) so that it does not
  raise an expection if ``setwinsize()`` fails. Some platforms such as Cygwin
  do not like setwinsize. This was a constant problem and since it is not a
  critical feature I decided to just silence the error.  Normally I don't like
  to do that, but in this case I'm making an exception.
* Added a method ``close()`` that does what you think. It closes the file
  descriptor of the child application. It makes no attempt to actually kill the
  child or wait for its status.
* Add variables ``__version__`` and ``__revision__`` (from cvs) to the pexpect
  modules.  This is mainly helpful to me so that I can make sure that I'm testing
  with the right version instead of one already installed.
* ``log_open()`` and ``log_close(`` have been removed. Now use ``setlog()``.
  The ``setlog()`` method takes a file object. This is far more flexible than
  the previous log method. Each time data is written to the file object it will
  be flushed. To turn logging off simply call ``setlog()`` with None.
* renamed the ``isAlive()`` method to ``isalive()`` to match the more typical
  naming style in Python. Also the technique used to detect child process
  status has been drastically modified. Previously I did some funky stuff
  with signals which caused indigestion in other Python modules on some
  platforms. It was a big headache. It still is, but I think it works
  better now.
* attribute ``matched`` renamed to ``after``
* new attribute ``match``
* The ``expect_eof()`` method is gone. You can now simply use the
  ``expect()`` method to look for EOF.
* **Pexpect works on OS X**, but the nature of the quirks cause many of the
  tests to fail. See bugs. (Incomplete Child Output). The problem is more
  than minor, but Pexpect is still more than useful for most tasks.
* **Solaris**: For some reason, the *second* time a pty file descriptor is created and
  deleted it never gets returned for use. It does not effect the first time
  or the third time or any time after that. It's only the second time. This
  is weird... This could be a file descriptor leak, or it could be some
  peculiarity of how Solaris recycles them. I thought it was a UNIX requirement
  for the OS to give you the lowest available filedescriptor number. In any case,
  this should not be a problem unless you create hundreds of pexpect instances...
  It may also be a pty module bug.


Moves and forks
---------------

* Pexpect development used to be hosted on Sourceforge.
* In 2011, Thomas Kluyver forked pexpect as 'pexpect-u', to support
  Python 3. He later decided he had taken the wrong approach with this.
* In 2012, Noah Spurrier, the original author of Pexpect, moved the
  project to Github, but was still too busy to develop it much.
* In 2013, Thomas Kluyver and Jeff Quast forked Pexpect again, intending
  to call the new fork Pexpected. Noah Spurrier agreed to let them use
  the name Pexpect, so Pexpect versions 3 and above are based on this
  fork, which now lives `here on Github <https://github.com/pexpect/pexpect>`_.

