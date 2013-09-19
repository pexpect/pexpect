import warnings

warnings.warn("This module has been moved to pexpect.ANSI, please update imports.",
                ImportWarning)
del warnings

from pexpect.ANSI import *  # analysis:ignore