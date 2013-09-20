import warnings

warnings.warn("This module has been moved to pexpect.pxssh, please update imports.",
                ImportWarning)
del warnings

from pexpect.pxssh import *  # analysis:ignore