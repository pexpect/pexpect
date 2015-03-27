""" Test __str__ methods. """
import pexpect

from . import PexpectTestCase


class TestCaseMisc(PexpectTestCase.PexpectTestCase):

    def test_str_spawnu(self):
        """ Exercise spawnu.__str__() """
        # given,
        p = pexpect.spawnu('cat')
        # exercise,
        value = str(p)
        # verify
        assert isinstance(value, str)

    def test_str_spawn(self):
        """ Exercise spawn.__str__() """
        # given,
        p = pexpect.spawn('cat')
        # exercise,
        value = str(p)
        # verify
        assert isinstance(value, str)

