#!/usr/bin/env python
""" This runs netstat on the remote host and returns stats about the
number of inet socket connections.

./topip.py [-s server_hostname] [-u username] [-p password] {-a N}
    -s : hostname of the remote server to login to.
    -u : username to user for login.
    -p : password to user for login.
    -n : print stddev for the the number of the top 'N' ipaddresses.
    -v : verbose - print stats and list of top ipaddresses.
    -a : send alert if stddev goes over 20.
Example:
    This will print stats for the top IP addresses connected to the given host:
        ./topip.py -s www.example.com -u mylogin -p mypassword -n 10 -v

"""
import os, sys, time, re, getopt, pickle, getpass, smtplib
import traceback
import pexpect, pxssh
from pprint import pprint

def exit_with_usage():
  #  print globals()['__doc__']
    os._exit(1)

def stats(r):
    """This returns a dict of the median, average, standard deviation, min and max
of a sequence.
    """
    tot = sum(r)
    avg = tot/len(r)
    sdsq = sum([(i-avg)**2 for i in r])
    s = list(r)
    s.sort()
    return dict(zip(['avg', 'med', 'stddev', 'min', 'max'] , (s[len(s)//2], avg,
(sdsq/(len(r)-1 or 1))**.5, min(r), max(r))))

def send_alert (message, subject):
    message = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % ('robot@example.com','admin@example.com',subject) + message
    server = smtplib.SMTP('localhost')
    server.sendmail('robot@example.com','admin@example.com',message)
    server.quit()

def main():
    ######################################################################
    ## Parse the options, arguments, get ready, etc.
    ######################################################################
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h?vas:u:p:n:', ['help','h','?'])
    except Exception, e:
        print str(e)
        exit_with_usage()
    options = dict(optlist)
    if len(args) > 1:
        exit_with_usage()

    if [elem for elem in options if elem in ['-h','--h','-?','--?','--help']]:
        print "Help:"
        exit_with_usage()

    if '-s' in options:
        hostname = options['-s']
    else:
        hostname = raw_input('hostname: ')
    if '-u' in options:
        username = options['-u']
    else:
        username = raw_input('username: ')
    if '-p' in options:
        password = options['-p']
    else:
        password = getpass.getpass('password: ')
    if '-n' in options:
        average_n = int(options['-n'])
    else:
        average_n = None
    if '-v' in options:
        verbose = True
    else:
        verbose = False
    if '-a' in options:
        alert_flag = True
    else:
        alert_flag = False

    #
    # Login via SSH
    #
    p = pxssh.pxssh()
    p.login(hostname, username, password)
    p.sendline('netstat -n --inet')

    ips = {}
    try:
        while 1:
            i = p.expect([p.PROMPT,'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+?):(\S+)\s+.*?\r'])
            if i == 0:
                break
            k = p.match.groups()[4]
            if k in ips:
                ips[k] = ips[k] + 1
            else:
                ips[k] = 1
    except:
        pass
    ips = dict([ (key,value) for key,value in ips.items() if '192.168.' not in key])
    ips = dict([ (key,value) for key,value in ips.items() if '127.0.0.1' not in key])
    ips = dict([ (key,value) for key,value in ips.items() if '69.80.212.140' not in key]) # VI Direct
    ips = dict([ (key,value) for key,value in ips.items() if '67.101.112.26' not in key]) # Vinyl Interactive office
    ips = sorted(ips.iteritems(),lambda x,y:cmp(x[1], y[1]),reverse=True)
    if average_n <= 1:
        average_n = None
    s = stats(zip(*ips[0:average_n])[1]) # The * unary operator treats the list elements as arguments 
    s['maxip'] = ips[0]
    print s['stddev']
    if verbose:
        pprint (s)
        print
        pprint (ips[0:average_n])

    try:
        last_stats = pickle.load(file("/tmp/topip.last"))
    except:
        last_stats = {'maxip':None}

    if alert_flag:
        if s['stddev'] > 20 and s['maxip']==last_stats['maxip']:
            print
            print "SENDING ALERT"
            send_alert(str(s), "ALERT on %s" % hostname )

    pickle.dump(s, file("/tmp/topip.last","w"))
    p.logout()

if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        print str(e)
        traceback.print_exc()
        os._exit(1)

