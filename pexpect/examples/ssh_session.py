#
# Eric S. Raymond
#
from pexpect import *

class ssh_session:
    "Session with extra state including the password to be used."
    def __init__(self, user, host, password=None, verbose=0):
        self.user = user
        self.host = host
        self.verbose = verbose
        self.password = password
    def __exec(self, command):
        "Execute a command on the remote host.  Return the output."
        child = spawn(command)
        if self.verbose:
            sys.stderr.write("-> " + command + "\n")
        seen = child.expect(['assword:', EOF])
        if seen == 0:
            if not self.password:
                self.password = getpass.getpass('Remote password: ')
            child.sendline(self.password)
            seen = child.expect(EOF)
        if self.verbose:
            sys.stderr.write("<- " + child.before + "\n")
        return child.before
    def ssh(self, command):
        return self.__exec("ssh -l %s %s \"%s\""%(self.user,self.host,command))
    def scp(self, src, dst):
        return self.__exec("scp %s %s@%s:%s" % (src, session.user, session.host, dst))
    def exists(self, file):
        "Retrieve file permissions of specified remote file."
        seen = self.ssh("/bin/ls -ld %s" % file)
        if string.find(seen, "No such file") > -1:
            return None # File doesn't exist
        else:
            return seen.split()[0] # Return permission field of listing.
