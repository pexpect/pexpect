#!/usr/bin/env python
# #sys.path.insert (0,"/var/www/cgi-bin")
#sys.path.insert (0,"/usr/local/apache/cgi-bin")

import sys, os, socket, random, string, traceback, cgi

CGISH_HTML="""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title>%(TITLE)s</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<style type=text/css>
a {color: #9f9; text-decoration: none}
a:hover {color: #0f0}
hr {color: #0f0}
html,body,textarea,input,form
{
font-family: "Courier New", Courier, mono; 
font-size: 8pt; 
color: #0c0;
background-color: #030;
margin:0;
padding:0;
border:0;
}
input { background-color: #020; }
textarea {
border-width:1;
border-style:solid;
border-color:#0c0;
padding:3;
margin:3;
}
</style>

<script language="JavaScript">
function focus_first()
{if (document.forms.length > 0)
{var TForm = document.forms[0];
for (i=0;i<TForm.length;i++){
if ((TForm.elements[i].type=="text")||
(TForm.elements[i].type=="textarea")||
(TForm.elements[i].type.toString().charAt(0)=="s"))
{document.forms[0].elements[i].focus();break;}}}}

// JavaScript Virtual Keyboard
// If you like this code then buy me a sandwich.
// Noah Spurrier <noah@noah.org>
var flag_shift=0;
var flag_shiftlock=0;
var flag_ctrl=0;
var ButtonOnColor = "#ee0";

function init ()
{
    // hack to set quote key to show both single quote and double quote
    document.form['quote'].value = "'" + '  "';
    refresh_screen();
    document.form["command"].focus();
}

function loadurl(dest)
{ 
    xmlhttp = window.XMLHttpRequest?new XMLHttpRequest(): new ActiveXObject("Microsoft.XMLHTTP");
    xmlhttp.onreadystatechange = update_virtual_screen;
    xmlhttp.open("GET", dest);
    xmlhttp.setRequestHeader("If-Modified-Since", "Sat, 1 Jan 2000 00:00:00 GMT");
    xmlhttp.send(null);
}
function update_virtual_screen()
{
    if ((xmlhttp.readyState == 4) && (xmlhttp.status == 200))
    {
        var screen_text = xmlhttp.responseText;
        document.form["screen_text"].value = screen_text;
        //var json_data = json_parse(xmlhttp.responseText);
    }
}
function refresh_screen()
{
    loadurl('bd_client.cgi?ajax=refresh');
}
function query_cursor()
{
    loadurl('bd_client.cgi?ajax=cursor');
}

function type_key (chars)
{
    var ch = '?';
    if (flag_shiftlock || flag_shift)
    {
        ch = chars.substr(1,1);
    }
    else if (flag_ctrl)
    {
        ch = chars.substr(2,1);
    }
    else
    {
        ch = chars.substr(0,1);
    }
    loadurl('bd_client.cgi?ajax=send&arg=' + escape(ch));
    if (flag_shift || flag_ctrl)
    {
        flag_shift = 0;
        flag_ctrl = 0;
    }
    update_button_colors();
}

function key_shiftlock()
{
    flag_ctrl = 0;
    flag_shift = 0;
    if (flag_shiftlock)
    {
        flag_shiftlock = 0;
    }
    else
    {
        flag_shiftlock = 1;
    }
    update_button_colors();
}

function key_shift()
{
    if (flag_shift)
    {
        flag_shift = 0;
    }
    else
    {
        flag_ctrl = 0;
        flag_shiftlock = 0;
        flag_shift = 1;
    }
    update_button_colors(); 
}
function key_ctrl ()
{
    if (flag_ctrl)
    {
        flag_ctrl = 0;
    }
    else
    {
        flag_ctrl = 1;
        flag_shiftlock = 0;
        flag_shift = 0;
    }
    
    update_button_colors();
}
function update_button_colors ()
{
    if (flag_ctrl)
    {
        document.form['Ctrl'].style.backgroundColor = ButtonOnColor;
        document.form['Ctrl2'].style.backgroundColor = ButtonOnColor;
    }
    else
    {
        document.form['Ctrl'].style.backgroundColor = document.form.style.backgroundColor;
        document.form['Ctrl2'].style.backgroundColor = document.form.style.backgroundColor;
    }
    if (flag_shift)
    {
        document.form['Shift'].style.backgroundColor = ButtonOnColor;
        document.form['Shift2'].style.backgroundColor = ButtonOnColor;
    }
    else
    {
        document.form['Shift'].style.backgroundColor = document.form.style.backgroundColor;
        document.form['Shift2'].style.backgroundColor = document.form.style.backgroundColor;
    }
    if (flag_shiftlock)
    {
        document.form['ShiftLock'].style.backgroundColor = ButtonOnColor;
    }
    else
    {
        document.form['ShiftLock'].style.backgroundColor = document.form.style.backgroundColor;
    }
    
}
</script>

</head>

<!-- <body onLoad="firstFocus()"> -->
<body onload="init()">
<form id="form" name="form" action="/cgi-bin/bd_client.cgi" method="POST">
<input name="sid" value="%(SID)s" type="hidden">
<textarea name="screen_text" cols="80" rows="24">%(SHELL_OUTPUT)s</textarea>
<hr noshade="1">
&nbsp;<input name="command" id="command" type="text" size="80"><br>
<p align="left"> 
<table border="0" align="left">
<tr>
<td width="86%%" align="center">    
    <input name="submit" type="submit" value="Enter">
    <input name="esc" type="submit" value="ESC">
    <input name="refresh" type="button" value="REFRESH" onclick="refresh_screen()">
    <input name="refresh" type="button" value="CURSOR" onclick="query_cursor()">
    <br>
    <input type="button" value="Esc" onclick="type_key('\\x1b\\x1b')" />
    <input type="button" value="` ~" onclick="type_key('`~')" />
    <input type="button" value="1!" onclick="type_key('1!')" />
    <input type="button" value="2@" onclick="type_key('2@\\x00')" />
    <input type="button" value="3#" onclick="type_key('3#')" />
    <input type="button" value="4$" onclick="type_key('4$')" />
    <input type="button" value="5%%" onclick="type_key('5%%')" />
    <input type="button" value="6^" onclick="type_key('6^\\x1E')" />
    <input type="button" value="7&" onclick="type_key('7&')" />
    <input type="button" value="8*" onclick="type_key('8*')" />
    <input type="button" value="9(" onclick="type_key('9(')" />
    <input type="button" value="0)" onclick="type_key('0)')" />
    <input type="button" value="-_" onclick="type_key('-_\\x1F')" />
    <input type="button" value="=+" onclick="type_key('=+')" />
    <input type="button" value="BkSp" onclick="type_key('\\x08\\x08\\x08')" />
    <br>
    <input type="button" value="Tab" onclick="type_key('\\t\\t')" />
    <input type="button" value="Q" onclick="type_key('qQ\\x11')" />
    <input type="button" value="W" onclick="type_key('wW\\x17')" />
    <input type="button" value="E" onclick="type_key('eE\\x05')" />
    <input type="button" value="R" onclick="type_key('rR\\x12')" />
    <input type="button" value="T" onclick="type_key('tT\\x14')" />
    <input type="button" value="Y" onclick="type_key('yY\\x19')" />
    <input type="button" value="U" onclick="type_key('uU\\x15')" />
    <input type="button" value="I" onclick="type_key('iI\\x09')" />
    <input type="button" value="O" onclick="type_key('oO\\x0F')" />
    <input type="button" value="P" onclick="type_key('pP\\x10')" />
    <input type="button" value="[ {" onclick="type_key('[{\\x1b')" />
    <input type="button" value="] }" onclick="type_key(']}\\x1d')" />
    <input type="button" value="\\ |" onclick="type_key('\\\\|\\x1c')" />
    <br>
    <input type="button" id="Ctrl" value="Ctrl" onclick="key_ctrl()" />
    <input type="button" value="A" onclick="type_key('aA\\x01')" />
    <input type="button" value="S" onclick="type_key('sS\\x13')" />
    <input type="button" value="D" onclick="type_key('dD\\x04')" />
    <input type="button" value="F" onclick="type_key('fF\\x06')" />
    <input type="button" value="G" onclick="type_key('gG\\x07')" />
    <input type="button" value="H" onclick="type_key('hH\\x08')" />
    <input type="button" value="J" onclick="type_key('jJ\\x0A')" />
    <input type="button" value="K" onclick="type_key('kK\\x0B')" />
    <input type="button" value="L" onclick="type_key('lL\\x0C')" />
    <input type="button" value="; :" onclick="type_key(';:')" />
    <input type="button" id="quote" value="'" onclick="type_key('\\x27\\x22')" />
    <input type="button" value="Enter" onclick="type_key('\\n\\n')" />
    <br>
    <input type="button" id="ShiftLock" value="Caps Lock" onclick="key_shiftlock()" />
    <input type="button" id="Shift" value="Shift" onclick="key_shift()"  />
    <input type="button" value="Z" onclick="type_key('zZ\\x1A')" />
    <input type="button" value="X" onclick="type_key('xX\\x18')" />
    <input type="button" value="C" onclick="type_key('cC\\x03')" />
    <input type="button" value="V" onclick="type_key('vV\\x16')" />
    <input type="button" value="B" onclick="type_key('bB\\x02')" />
    <input type="button" value="N" onclick="type_key('nN\\x0E')" />
    <input type="button" value="M" onclick="type_key('mM\\x0D')" />
    <input type="button" value=", <" onclick="type_key(',<')" />
    <input type="button" value=". >" onclick="type_key('.>')" />
    <input type="button" value="/ ?" onclick="type_key('/?')" />
    <input type="button" id="Shift2" value="Shift" onclick="key_shift()" />
    <input type="button" id="Ctrl2" value="Ctrl" onclick="key_ctrl()" />
    <br>
    <input type="button" value="        FINAL FRONTIER        " onclick="type_key('  ')" />
</td>
</tr>
</table>  
</p>

</form>
</body>
</html>
"""

def random_sid ():
    a=random.randint(0,65535)
    b=random.randint(0,65535)
    return 'pxssh%04x%04x' % (a,b)

def bd_client (command, host='localhost', port=-1):
    """This sends a request to the server and returns the response.
    If port is less than 0 then host is assumed
    to be the filename of a Unix domain socket.
    """
    if port < 0:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(host)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
    s.send(command)
    data = s.recv (2500)
    s.close()
    return data

print "Content-type: text/html;charset=utf-8\r\n"
sys.stderr = sys.stdout
ajax_mode = False
TITLE="Shell"
SHELL_OUTPUT=""
SID="NOT"
try:
    form = cgi.FieldStorage()
    if not form.has_key('sid'):
        SID=random_sid()
    else:
        SID=form['sid'].value
    if form.has_key('ajax'):
        ajax_mode = True
        ajax_cmd = form['ajax'].value
        if ajax_cmd == 'send':
            command = ':xsend'
            arg = form['arg'].value.encode('hex')
            result = bd_client (command + ' ' + arg, "/tmp/mysock")
            print result
        elif ajax_cmd == 'refresh':
            command = ':refresh'
            result = bd_client (command, "/tmp/mysock")
            print result
        elif ajax_cmd == 'cursor':
            command = ':cursor'
            result = bd_client (command, "/tmp/mysock")
            print result
    elif form.has_key('command'):
        command = form["command"].value
        SHELL_OUTPUT = bd_client (command, "/tmp/mysock")
        print CGISH_HTML % locals()
    else:
        print CGISH_HTML % locals()
except:
    tb_dump = traceback.format_exc()
    if ajax_mode:
        print str(tb_dump)
    else:
        SHELL_OUTPUT=str(tb_dump)
        print CGISH_HTML % locals()

