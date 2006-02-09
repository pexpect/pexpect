"""This is like pexpect.spawn but allows you to supply your own,
already open file descriptor. For example, you could use it to
read through a file looking for patterns, or to control a modem or
serial device.

"""
import pexpect

class fdspawn (pexpect.spawn):
    def __init__ (self, fd, args=[], timeout=30, maxread=2000, searchwindowsize=None, logfile=None):
        """This takes a file descriptor (an int) or an object that support the fileno() method
            (returning an int). All Python file-like objects support fileno().
        """
        ### TODO: Add better handling of trying to use fdspawn in place of spawn
        ### TODO: (overload to allow fdspawn to also handle commands as spawn does.
        if type(fd) == type(''):
            return

        if type(fd)!=type(1) and hasattr(fd, 'fileno'):
            fd = fd.fileno()
        pexpect.spawn.__init__(self, None, args, timeout, maxread, searchwindowsize, logfile)
        self.child_fd = fd
        self.own_fd = False
        self.closed = False

    def __del__ (self):
        return

    def close (self):
        if super(fdspawn, self).child_fd == -1:
            return
        if self.own_fd:
            super(fdspawn, self).close (self)
        else:
            self.flush()
            os.close(super(fdspawn, self).child_fd)
            self.child_fd = -1
            self.closed = True

    def isalive (self):
        print "isalive()"
        return True

    def terminate (self, force=False):
        print "terminate()"
        return

    def kill (self, sig):
        print "kill()"
        return

