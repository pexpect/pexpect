import warnings

warnings.warn("This module has been moved to pexpect.FSM, please update imports.",
                ImportWarning)
del warnings

from pexpect.FSM import *  # analysis:ignore