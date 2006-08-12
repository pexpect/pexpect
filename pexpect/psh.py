"""This is a utility class to make shell scripting easier in Python.
It combines Pexpect and wraps many Standard Python Library functions.
The goal is to make Python an attractive alternative to Sh scripting.
$Id$
"""
import pexpect, os, sys

class psh (object):
    def __init__ (self):
        self.cwd = os.getcwd()

    def ls (self, path=''):
    def cd (self, path='-'):
    def rm (self, path=''):
    def cp (self, path_from='', path_to=''):
    def mv (self, path_from='', path_to=''):
    def pwd (self):
    def which (self, exe_name):
    def chown (self, path, user='', group='', recurse=False):
    def chmod (self, path, perms='', recurse=False):
    def chattr (self, path, attrs='', recurse=False):
    def cat (self, path):
    def run (self, cmd):
    def pipe (self, cmd, string_to_send):
    
