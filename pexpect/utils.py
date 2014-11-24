import os
import stat


def is_executable_file(path):
    """Checks that path is an executable regular file (or a symlink to a file).

    This is roughly ``os.path isfile(path) and os.access(path, os.X_OK)``, but
    on some platforms :func:`os.access` gives us the wrong answer, so this
    checks permission bits directly.
    """
    # follow symlinks,
    fpath = os.path.realpath(path)

    # return False for non-files (directories, fifo, etc.)
    if not os.path.isfile(fpath):
        return False

    # On Solaris, etc., "If the process has appropriate privileges, an
    # implementation may indicate success for X_OK even if none of the
    # execute file permission bits are set."
    #
    # For this reason, it is necessary to explicitly check st_mode

    # get file mode using os.stat, and check if `other',
    # that is anybody, may read and execute.
    mode = os.stat(fpath).st_mode
    if mode & stat.S_IROTH and mode & stat.S_IXOTH:
        return True

    # get current user's group ids, and check if `group',
    # when matching ours, may read and execute.
    user_gids = os.getgroups() + [os.getgid()]
    if (os.stat(fpath).st_gid in user_gids and
            mode & stat.S_IRGRP and mode & stat.S_IXGRP):
        return True

    # finally, if file owner matches our effective userid,
    # check if `user', may read and execute.
    user_gids = os.getgroups() + [os.getgid()]
    if (os.stat(fpath).st_uid == os.geteuid() and
            mode & stat.S_IRUSR and mode & stat.S_IXUSR):
        return True

    return False

def which(filename):
    '''This takes a given filename; tries to find it in the environment path;
    then checks if it is executable. This returns the full path to the filename
    if found and executable. Otherwise this returns None.'''

    # Special case where filename contains an explicit path.
    if os.path.dirname(filename) != '' and is_executable_file(filename):
        return filename
    if 'PATH' not in os.environ or os.environ['PATH'] == '':
        p = os.defpath
    else:
        p = os.environ['PATH']
    pathlist = p.split(os.pathsep)
    for path in pathlist:
        ff = os.path.join(path, filename)
        if is_executable_file(ff):
            return ff
    return None


def split_command_line(command_line):

    '''This splits a command line into a list of arguments. It splits arguments
    on spaces, but handles embedded quotes, doublequotes, and escaped
    characters. It's impossible to do this with a regular expression, so I
    wrote a little state machine to parse the command line. '''

    arg_list = []
    arg = ''

    # Constants to name the states we can be in.
    state_basic = 0
    state_esc = 1
    state_singlequote = 2
    state_doublequote = 3
    # The state when consuming whitespace between commands.
    state_whitespace = 4
    state = state_basic

    for c in command_line:
        if state == state_basic or state == state_whitespace:
            if c == '\\':
                # Escape the next character
                state = state_esc
            elif c == r"'":
                # Handle single quote
                state = state_singlequote
            elif c == r'"':
                # Handle double quote
                state = state_doublequote
            elif c.isspace():
                # Add arg to arg_list if we aren't in the middle of whitespace.
                if state == state_whitespace:
                    # Do nothing.
                    None
                else:
                    arg_list.append(arg)
                    arg = ''
                    state = state_whitespace
            else:
                arg = arg + c
                state = state_basic
        elif state == state_esc:
            arg = arg + c
            state = state_basic
        elif state == state_singlequote:
            if c == r"'":
                state = state_basic
            else:
                arg = arg + c
        elif state == state_doublequote:
            if c == r'"':
                state = state_basic
            else:
                arg = arg + c

    if arg != '':
        arg_list.append(arg)
    return arg_list
