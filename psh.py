import warnings

warnings.warn("This module has been moved to pexpect.psh, please update imports.",
                ImportWarning)
del warnings

from pexpect.psh import *  # analysis:ignore