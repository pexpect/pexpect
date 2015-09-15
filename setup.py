from distutils.core import setup
import os
import re

with open(os.path.join(os.path.dirname(__file__), 'pexpect', '__init__.py'), 'r') as f:
    for line in f:
        version_match = re.search(r"__version__ = ['\"]([^'\"]*)['\"]", line)
        if version_match:
            version = version_match.group(1)
            break
    else:
        raise Exception("couldn't find version number")

long_description = """
Pexpect is a pure Python module for spawning child applications; controlling
them; and responding to expected patterns in their output. Pexpect works like
Don Libes' Expect. Pexpect allows your script to spawn a child application and
control it as if a human were typing commands.

Pexpect can be used for automating interactive applications such as ssh, ftp,
passwd, telnet, etc. It can be used to a automate setup scripts for duplicating
software package installations on different servers. It can be used for
automated software testing. Pexpect is in the spirit of Don Libes' Expect, but
Pexpect is pure Python. Unlike other Expect-like modules for Python, Pexpect
does not require TCL or Expect nor does it require C extensions to be compiled.
It should work on any platform that supports the standard Python pty module.
The Pexpect interface was designed to be easy to use.
"""

setup (name='pexpect',
    version=version,
    packages=['pexpect'],
    description='Pexpect allows easy control of interactive console applications.',
    long_description=long_description,
    author='Noah Spurrier; Thomas Kluyver; Jeff Quast',
    author_email='noah@noah.org; thomas@kluyver.me.uk; contact@jeffquast.com',
    url='http://pexpect.readthedocs.org/',
    license='ISC license',
    platforms='UNIX',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: System',
        'Topic :: System :: Archiving :: Packaging',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Shells',
        'Topic :: System :: Software Distribution',
        'Topic :: Terminals',
    ],
    install_requires=['ptyprocess>=0.5'],
)
