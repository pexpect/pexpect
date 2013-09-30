History
=======

Releases
--------

Version 3.0
```````````

The new major version number doesn't indicate any deliberate API incompatibility.
We have endeavoured to avoid breaking existing APIs. However, pexpect is under
new maintenance after a long dormancy, so some caution is warranted.

* A new :ref:`unicode API <unicode>` was introduced.
* Python 3 is now supported, using a single codebase.
* Pexpect now requires at least Python 2.6 or 3.2.

We also now have `docs on ReadTheDocs <http://pexpect.readthedocs.org/>`_,
and `continuous integration on Travis CI <https://travis-ci.org/pexpect/pexpect>`_.

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

