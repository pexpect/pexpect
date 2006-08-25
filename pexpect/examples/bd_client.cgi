#!/usr/bin/env python
"""Back door shell server

This exposes a shell terminal on a socket.

    --hostname : sets the remote host name to open an ssh connection to.
    --username : sets the user name to login with
    --password : (optional) sets the password to login with
    --port     : set the local port for the server to listen on
    --watch    : show the virtual screen after each client request

This project is probably not the most security concious thing I've ever built.
This should be considered an experimental tool -- at best.
"""
import sys,os
sys.path.insert (0,os.getcwd())
import socket, random, string, traceback, cgi, time, getopt, getpass, threading,resource,signal
import pxssh, pexpect, ANSI

def exit_with_usage(exit_code=1):
    print globals()['__doc__']
    os._exit(exit_code)

def client (command, host='localhost', port=-1):
    """This sends a request to the server and returns the response.
    If port is <= 0 then host is assumed to be the filename of a Unix domain socket.
    If port is greater 0 then host is an inet hostname.
    """
    if port <= 0:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(host)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
    s.send(command)
    data = s.recv (2500)
    s.close()
    return data

def server (hostname, username, password, socket_filename='/tmp/mysock', daemon_mode = True, verbose=False):
    """This starts and services requests from the client.
    """
    if daemon_mode:
        d = daemonize()
        if d != 0:
            return d

    if verbose: sys.stdout.write ('server started with pid %d\n' % os.getpid() )

    virtual_screen = ANSI.ANSI (24,80) 
    child = pxssh.pxssh()
    child.login (hostname, username, password)
    if verbose: print 'created shell. command line prompt is', child.PROMPT
    virtual_screen.write (child.before)
    virtual_screen.write (child.after)

    if os.path.exists(socket_filename): os.remove(socket_filename)
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.bind(socket_filename)
    os.chmod(socket_filename,0777)
    if verbose: print 'Listen'
    s.listen(1)
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #localhost = '127.0.0.1'
    #s.bind((localhost, port))
    #print 'Listen'
    #s.listen(1)

    r = roller (0.01, endless_poll, (child, child.PROMPT, virtual_screen))
    r.start()
    if verbose: print "screen poll updater started in background thread"
    sys.stdout.flush()
    try:
        while True:
            conn, addr = s.accept()
            if verbose: print 'Connected by', addr
            data = conn.recv(1024)
            file('/tmp/PXLOG','a').write('data='+str(data)+'\n')
            if data[0]!=':':
                cmd = ':sendline'
                arg = data.strip()
            else:
                request = data.split(' ', 1)
                if len(request)>1:
                    cmd = request[0].strip()
                    arg = request[1].strip()
                else:
                    cmd = request[0].strip()
            if cmd == ':exit':
                r.cancel()
                break
            elif cmd == ':sendline':
                file('/tmp/PXLOG','a').write("sendline arg: " + str(arg)+'\n')
                child.sendline (arg)
                #child.prompt(timeout=2)
                time.sleep(0.2)
                shell_window = str(virtual_screen)
                file('/tmp/PXLOG','a').write("virtual_screen : " + str(virtual_screen)+'\n')
            elif cmd == ':send' or cmd==':xsend':
                if cmd==':xsend':
                    arg = arg.decode("hex")
                child.send (arg)
                time.sleep(0.2)
                shell_window = str(virtual_screen)
            elif cmd == ':cursor':
                shell_window = '%x%x' % (virtual_screen.cur_r, virtual_screen.cur_c)
            elif cmd == ':refresh':
                shell_window = str(virtual_screen)

            file('/tmp/PXLOG','a').write("sending response " + '\n')
            response = []
            response.append (shell_window)
            #response = add_cursor_blink (response, row, col)
            if verbose: print '\n'.join(response)
            sent = conn.send('\n'.join(response))
            file('/tmp/PXLOG','a').write("sent response " + '\n')
            if sent < len (response):
                if verbose: print "Sent is too short. Some data was cut off."
            conn.close()
    except e:
        file('/tmp/PXLOG','a').write(str(e)+'\n')
        r.cancel()
        if verbose: print "cleaning up socket"
        s.close()
        if os.path.exists(socket_filename): os.remove(socket_filename)
        if verbose: print "server done!"

class roller (threading.Thread):
    """This class continuously loops a function in a thread.
    """
    def __init__(self, interval, function, args=[], kwargs={}):
        """The interval parameter defines time between each call to the function.
        """
        threading.Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = threading.Event()
    def cancel(self):
        """Stop the roller."""
        self.finished.set()
    def run(self):
        while not self.finished.isSet():
            # self.finished.wait(self.interval)
            self.function(*self.args, **self.kwargs)

def endless_poll (child, prompt, screen, refresh_timeout=0.1):
    """This keeps the screen updated with the output of the child.
        This runs in a separate thread.
        See roller class.
    """
    #child.logfile_read = screen
    try:
        s = child.read_nonblocking(4000, 0.1)
        screen.write(s)
    except:
        pass

def daemonize (stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    '''This forks the current process into a daemon.
    Almost none of this is necessary (or advisable) if your daemon 
    is being started by inetd. In that case, stdin, stdout and stderr are 
    all set up for you to refer to the network connection, and the fork()s 
    and session manipulation should not be done (to avoid confusing inetd). 
    Only the chdir() and umask() steps remain as useful. 

    References:
        UNIX Programming FAQ
        1.7 How do I get my program to act like a daemon?
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16

        Advanced Programming in the Unix Environment
        W. Richard Stevens, 1992, Addison-Wesley, ISBN 0-201-56317-7.

    The stdin, stdout, and stderr arguments are file names that
    will be opened and be used to replace the standard file descriptors
    in sys.stdin, sys.stdout, and sys.stderr.
    These arguments are optional and default to /dev/null.
    Note that stderr is opened unbuffered, so
    if it shares a file with stdout then interleaved output
    may not appear in the order that you expect.
    '''

    # Do first fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            return -1
            #os._exit(0)   # Exit first parent.
    except OSError, e: 
        sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror) )
        os._exit(1)

    # Decouple from parent environment.
    os.chdir("/") 
    os.umask(0) 
    os.setsid() 

    # Do second fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            time.sleep(4)
            #sys.stderr.close()
            #sys.stdout.close()
      #      os._exit(0)   # Exit second parent.
      #      sys.exit(0)
            return -2
    except OSError, e: 
        sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) )
        os._exit(1)

    # Now I am a daemon!
    
    # Redirect standard file descriptors.
    si = open(stdin, 'r')
    so = open(stdout, 'a+')
    se = open(stderr, 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    # return as the daemon
    return 0

def random_sid ():
    a=random.randint(0,65535)
    b=random.randint(0,65535)
    return '%04x%04x.sid' % (a,b)

def parse_host_connect_string (hcs):
    """This parses a host connection string in the form
    username:password@hostname:port. All fields are options expcet hostname. A
    dictionary is returned with all four keys. Keys that were not included are
    set to empty strings ''. Note that if your password has the '@' character
    then you must backslash escape it.
    """
    if '@' in hcs:
        p = re.compile (r'(?P<username>[^@:]*)(:?)(?P<password>.*)(?!\\)@(?P<hostname>[^:]*):?(?P<port>[0-9]*)')
    else:
        p = re.compile (r'(?P<username>)(?P<password>)(?P<hostname>[^:]*):?(?P<port>[0-9]*)')
    m = p.search (hcs)
    d = m.groupdict()
    d['password'] = d['password'].replace('\\@','@')
    return d
     
def pretty_box (s, rows=24, cols=80):
    """This puts an ASCII text box around the given string.
    """
    top_bot = '+' + '-'*cols + '+\n'
    return top_bot + '\n'.join(['|'+line+'|' for line in s.split('\n')]) + '\n' + top_bot
    
def client_cgi ():
    """This handles the request if this script was called as a cgi.
    """
    sys.stderr = sys.stdout
    ajax_mode = False
    TITLE="Shell"
    SHELL_OUTPUT=""
    SID="NOT"
    try:
        form = cgi.FieldStorage()
        if form.has_key('ajax'):
            ajax_mode = True
            ajax_cmd = form['ajax'].value
            SID=form['sid'].value
            if ajax_cmd == 'send':
                command = ':xsend'
                arg = form['arg'].value.encode('hex')
                result = client (command + ' ' + arg, '/tmp/'+SID)
                print "Content-type: text/html;charset=utf-8\r\n"
                print result
            elif ajax_cmd == 'refresh':
                command = ':refresh'
                result = client (command, '/tmp/'+SID)
                print "Content-type: text/html;charset=utf-8\r\n"
                print result
            elif ajax_cmd == 'cursor':
                command = ':cursor'
                result = client (command, '/tmp/'+SID)
                print "Content-type: text/html;charset=utf-8\r\n"
                print result
        elif not form.has_key('sid'):
            SID=random_sid()
            print "Content-type: text/html;charset=utf-8\r\n"
            print LOGIN_HTML % locals();
        else:
            SID=form['sid'].value
            if form.has_key('start_server'):
                USERNAME = form['username'].value
                PASSWORD = form['password'].value
                d = server ('127.0.0.1', USERNAME, PASSWORD, '/tmp/'+SID)
                if d==-2:
                    return -2
                if d==-1:
                    SHELL_OUTPUT='hit refresh'
            else:
                if form.has_key('command'):
                    command = form['command'].value
                else:
                    command = ''
                SHELL_OUTPUT = client (command, '/tmp/'+SID)
            print "Content-type: text/html;charset=utf-8\r\n"
            print CGISH_HTML % locals()
    except:
        tb_dump = traceback.format_exc()
        if ajax_mode:
            print str(tb_dump)
        else:
            SHELL_OUTPUT=str(tb_dump)
            print CGISH_HTML % locals()

def server_cli():
    """This is the command line interface to starting the server.
    This handles things if the script was not called as a CGI
    (if you run it from the command line).
    """
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h?d', ['help','h','?', 'hostname=', 'username=', 'password=', 'port=', 'watch'])
    except Exception, e:
        print str(e)
        exit_with_usage()

    command_line_options = dict(optlist)
    options = dict(optlist)
    # There are a million ways to cry for help. These are but a few of them.
    if [elem for elem in command_line_options if elem in ['-h','--h','-?','--?','--help']]:
        exit_with_usage(0)
  
    hostname = "127.0.0.1"
    #port = 1664
    username = os.getenv('USER')
    password = ""
    daemon_mode = False
    if '-d' in options:
        daemon_mode = True
    if '--watch' in options:
        watch_mode = True
    else:
        watch_mode = False
    if '--hostname' in options:
        hostname = options['--hostname']
    if '--port' in options:
        port = int(options['--port'])
    if '--username' in options:
        username = options['--username']
    if '--password' in options:
        password = options['--password']
    else:
        password = getpass.getpass('password: ')
   
    server (hostname, username, password, '/tmp/mysock', daemon_mode)

def main ():
    if os.getenv('REQUEST_METHOD') is None:
        server_cli()
    else:
        client_cgi()

# It's mostly HTML and Javascript from here on out.
CGISH_HTML="""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<title>%(TITLE)s %(SID)s</title>
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
    //refresh_screen();
    document.form["command"].focus();
}
function get_password ()
{
    var username = prompt("username?","");
    var password = prompt("password?","");
    start_server (username, password);
}
function multibrowser_ajax ()
{
    var xmlHttp = false;
/*@cc_on @*/
/*@if (@_jscript_version >= 5)
    try
    {
        xmlHttp = new ActiveXObject("Msxml2.XMLHTTP");
    }
    catch (e)
    {
        try
        {
            xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
        }
        catch (e2)
        {
              xmlHttp = false;
        }
    }
@end @*/

    if (!xmlHttp && typeof XMLHttpRequest != 'undefined')
    {
        xmlHttp = new XMLHttpRequest();
    }
    return xmlHttp;
}
function loadurl(dest)
{ 
    xmlhttp = multibrowser_ajax();
    //window.XMLHttpRequest?new XMLHttpRequest(): new ActiveXObject("Microsoft.XMLHTTP");
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
//function start_server (username, password)
//{
//    loadurl('bd_client.cgi?ajax=serverstart&username=' + escape(username) + '&password=' + escape(password);
//}
function refresh_screen()
{
    loadurl('bd_client.cgi?ajax=refresh&sid=%(SID)s');
}
function query_cursor()
{
    loadurl('bd_client.cgi?ajax=cursor&sid=%(SID)s');
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
    loadurl('bd_client.cgi?ajax=send&sid=%(SID)s&arg=' + escape(ch));
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
function keyHandler(e)
{
    var pressedKey;
    if (document.all)    { e = window.event; }
    if (document.layers) { pressedKey = e.which; }
    if (document.all)    { pressedKey = e.keyCode; }
    pressedCharacter = String.fromCharCode(pressedKey);
    type_key(pressedCharacter+pressedCharacter+pressedCharacter);
    alert(pressedCharacter);
//    alert(' Character = ' + pressedCharacter + ' [Decimal value = ' + pressedKey + ']');
}
//document.onkeypress = keyHandler;
//if (document.layers)
//    document.captureEvents(Event.KEYPRESS);
//http://sniptools.com/jskeys
//document.onkeyup = KeyCheck;       
function KeyCheck(e)
{
    var KeyID = (window.event) ? event.keyCode : e.keyCode;
    type_key(String.fromCharCode(KeyID));
    e.cancelBubble = true;
    window.event.cancelBubble = true;
}
</script>

</head>

<body onload="init()">
<form id="form" name="form" action="/cgi-bin/bd_client.cgi" method="POST">
<input name="sid" value="%(SID)s" type="hidden">
<textarea name="screen_text" cols="81" rows="25">%(SHELL_OUTPUT)s</textarea>
<hr noshade="1">
&nbsp;<input name="command" id="command" type="text" size="80"><br>
<table border="0" align="left">
<tr>
<td width="86%%" align="center">    
    <input name="submit" type="submit" value="Enter">
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
</form>
<hr>
</body>
</html>
"""

LOGIN_HTML="""<html>
<head>
<title>Shell Login</title>
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
function init ()
{
    document.login_form["username"].focus();
}
</script>
</head>
<body onload="init()">
<form name="login_form" method="POST">
<input name="start_server" value="1" type="hidden">
<input name="sid" value="%(SID)s" type="hidden">
username: <input name="username" type="text" size="20"><br>
password: <input name="password" type="text" size="20"><br>
<input name="submit" type="submit" value="enter">
</form>
<br>
/tmp/%(SID)s
</body>
</html>
"""

if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        print str(e)
        tb_dump = traceback.format_exc()
        print str(tb_dump)

