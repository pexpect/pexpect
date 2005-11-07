#!/usr/bin/env python

import os, time, pexpect

def getProcessResults(cmd, timeLimit=20):
  """
  executes 'cmd' as a child process and returns the child's output,
  the duration of execution, and the process exit status. Aborts if
  child process does not generate output for 'timeLimit' seconds.
  """
  output = ""
  startTime = time.time()
  child = pexpect.spawn(cmd)

  while 1:
    try:
      # read_nonblocking will add to 'outout' one byte at a time
      # newlines can show up as '\r\n' so we kill any '\r's which
      # will mess up the formatting for the viewer
      output += child.read_nonblocking(timeout=timeLimit).replace("\r","")
    except pexpect.EOF:
      # process terminated normally
      break
    except pexpect.TIMEOUT:
      output += "\nProcess aborted by FlashTest after %s seconds.\n" % timeLimit
      child.kill(9)
      break

  endTime = time.time()
  child.close(force=True)

  duration = endTime - startTime
  exitStatus = child.exitstatus

  return (output, duration, exitStatus)

cmd = "./ticker.py"

result, duration, exitStatus = getProcessResults(cmd)

print "result: %s" % result
print "duration: %s" % duration
print "exit-status: %s" % exitStatus


