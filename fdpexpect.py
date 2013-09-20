import warnings

warnings.warn("This module has been moved to pexpect.fdpexpect, please update imports.",
                ImportWarning)
del warnings

from pexpect.fdpexpect import *  # analysis:ignore