#!/usr/bin/env python
"""This runs testall.py on many different platforms running on the Compile Farm (cf.sourceforge.net).
"""
import pexpect
import sys
import getpass

def test_platform (platform_menu, platform_python_path):
	try:
		s = pexpect.spawn ('ssh noah@cf.sourceforge.net')
		s.setlog (sys.stdout)
		i = s.expect (['password:', 'yes/no'])
		if i == 1:
			s.sendline ('yes')
			s.expect ('password')
		s.sendline (PASSWORD)
		s.expect ('Choose compile farm server')
		s.sendline (platform_menu)
		s.expect_exact ('$')
		s.sendline ('cd pexpect')
		s.expect_exact ('$')
		s.sendline ('. ./cvs.conf')
		s.expect_exact ('$')
		s.sendline ('cvs up -d')
		s.expect ('password:')
		s.sendline (PASSWORD)
		s.expect_exact ('$')
		s.sendline (platform_python_path)
		i = s.expect_exact (['OK','$'], timeout=900) # Tests should not run more than 15 minutes.
		if i != 0:
			RESULT = s.before
		else:
			RESULT = 'OK!'
		s.sendline ('exit')
		s.sendline ('x')
		s.close()
	except Exception, e:
		return 'Exception in platform test: ' + str(e)
	return RESULT

PASSWORD = getpass.getpass('password: ')
results = []
result = test_platform ('H', 'python tools/testall.py')
results.append (('H', '[PPC - G4] MacOS X 10.1 SERVER Edition', result))
result = test_platform ('L', 'python tools/testall.py')
results.append (('L', '[Sparc - Ultra60] Linux 2.4 (Debian 3.0)', result))
result = test_platform ('B', 'python2 tools/testall.py')
results.append (('B', '[x86] Linux 2.4 (Redhat 7.3)', result))
result = test_platform ('M', '../Python-2.2.1/python tools/testall.py')
results.append (('M', '[Sparc - R220] Sun Solaris (8) #1', result))
result = test_platform ('G', 'python tools/testall.py')
results.append (('G', '[Alpha] Linux 2.2 (Debian 3.0)', result))
print results

