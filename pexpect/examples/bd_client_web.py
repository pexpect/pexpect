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

def page (result = ''):
	"""Return the main form"""
	return """<html>
		<head>
		<title>Og.</title>
<script language="JavaScript"> 
function firstFocus()
{
   if (document.forms.length > 0)
   {
      var TForm = document.forms[0];
      for (i=0;i<TForm.length;i++)
      {
         if ((TForm.elements[i].type=="text")||
           (TForm.elements[i].type=="textarea")||
           (TForm.elements[i].type.toString().charAt(0)=="s"))
         {
            document.forms[0].elements[i].focus();
            break;
         }
      }
   }
}
</script>
</head>
<body onLoad="firstFocus()">
<hr noshade="1">
<pre>
%s
</pre>
<hr noshade="1">
<form action="http://www.chocho.org/cgi-bin/bd_client_web.py" method="POST">
<input name="command" type="text" size="80">
<input name="submit" type="submit" value="Enter">
</form>
</body>
</html>
		""" % (result)

def bd_client (command, host='localhost', port = 1666):
	HOST = 'localhost'    # The remote host
	PORT = 1666              # The same port as used by the server
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	s.send(command)
	data = s.recv(1024)
	s.close()
	return data

	#fout = file ('/tmp/log2','w')
	#fout.write (command)
	#fout.write ('\n')
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	s.send(command)
	data = s.recv(1024)
	#fout.write (data)
	#fout.write ('\n')
	s.close()
	#fout.close()
	return data

#def link (matchobject):
#	"""Used in re.sub calls to replace a matched object with an HTML link."""
#	path = matchobject.group(0)
#	l = "<a href=\"http://63.199.26.227/cgi-bin/ls.py?root=%s&path=%s\">%s</a>" % \
#		(ROOTPATH+"/"+path, ROOTPATH+"/"+path, path)
#	return l

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

sys.path.insert (0,"/usr/local/apache/cgi-bin")
sys.stderr = sys.stdout

print "Content-type: text/html"
print

try:
	form = cgi.FieldStorage()
	if form.has_key("command"):
		command = form["command"].value
		result = bd_client (command)
		print page(result)
	else:
		print page()

except:
	print "\n\n<pre>"
	traceback.print_exc()
	print "</pre>"


