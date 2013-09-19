import warnings

warnings.warn("This module has been moved to pexpect.screen, please update imports.",
                ImportWarning)
del warnings

from pexpect.screen import *  # analysis:ignore