#!/usr/bin/env python
"""Script
"""

import os, sys, time, getopt
import traceback
import pexpect

def exit_with_usage():
    print globals()['__doc__']
    os._exit(1)

def main():
    ######################################################################
    ## Parse the options, arguments, etc.
    ######################################################################
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'h?rdb', ['help','t=','f=','u=','p=','r1=','r2=','svnurl=','rdiff=','allowconf','check_appver', 'qr', 'qd'])
    except Exception, e:
        print str(e)
        exit_with_usage()
    options = dict(optlist)
    if len(options)==0 and len(args)==0:
        exit_with_usage()
    if [elem for elem in options if elem in ['-h','--h','-?','--?','--help']]:
        print "Help:"
        exit_with_usage()

    ######################################################################
    ## Create script log file and start interative command.
    ######################################################################
    fout = file ("script.log", "w")
    fout.write ("# "+nowdatestring()+"\n")
    p = spawn("bash")
    p.logfile = fout
    p.interact()
    fout.close()

def nowdatestring ():
    """This returns date/time in the form CCCCyymm.hhmmss
    """
    parts = time.localtime()
    return '%4d%02d%02d.%02d%02d%02d' % parts[:-3]

if __name__ == "__main__":
    try:
        main ()
    except Exception, e:
        print "ERROR"
        print str(e)
        annoy_the_human_with_incessant_beeping()
        traceback.print_exc()
        os._exit(1)

