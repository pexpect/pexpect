#!/usr/bin/env python
'''This demonstrates controlling a screen oriented application (curses).
It starts two instances of gnuchess and then pits them against each other.
'''
import pexpect
import string

REGEX_MOVE = '(?:[a-z]|\x1b\[C)(?:[0-9]|\x1b\[C)(?:[a-z]|\x1b\[C)(?:[0-9]|\x1b\[C)'
REGEX_MOVE_PART = '(?:[0-9]|\x1b\[C)(?:[a-z]|\x1b\[C)(?:[0-9]|\x1b\[C)'

class Chess:

	def __init__(self, engine = "/usr/local/bin/gnuchess -a -h 1"):
		self.child = pexpect.spawn (engine)
		self.child.expect ('Chess')
		if self.child.matched != 'Chess':
			raise IOError, 'incompatible chess program'
		self.last_computer_move = ''

	def do_first_move (self, move):
		self.child.expect ('Your move is')
		self.child.sendline (move)
#		print '', self.child.matched
		return move

	def do_move (self, move):
		self.child.expect ('\[19;60H')
		self.child.sendline (move)
		print 'do_move', self.child.matched, move
		return move

	def get_first_computer_move (self):
		self.child.expect ('My move is')
		self.child.expect (REGEX_MOVE)
#		print '', self.child.matched
		return self.child.matched
	
	def get_computer_move (self):
		print 'Here'
		i = self.child.expect (['\[17;59H', '\[17;58H'])
		print i
		if i == 0:
			self.child.expect (REGEX_MOVE)
			if len(self.child.matched) < 4:
				self.child.matched = self.child.matched + self.last_computer_move[3]
		if i == 1:
			self.child.expect (REGEX_MOVE_PART)
			self.child.matched = self.last_computer_move[0] + self.child.matched
		print '', self.child.matched
		self.last_computer_move = self.child.matched
		return self.child.matched

	def switch (self):
		self.child.sendline ('switch')

	def set_depth (self, depth):
		self.child.sendline ('depth')
		self.child.expect ('depth=')
		self.child.sendline ('%d' % depth)

	def quit(self):
		self.child.sendline ('quit')
import sys, os
print 'Starting...'
white = Chess()
white.child.echo = 1
white.child.expect ('Your move is')
white.set_depth(2)
white.switch()

move_white = white.get_first_computer_move()
print 'first move white:', move_white

white.do_move ('e7e5')
move_white = white.get_computer_move()
print 'move white:', move_white
white.do_move ('f8c5')
move_white = white.get_computer_move()
print 'move white:', move_white
white.do_move ('b8a6')
move_white = white.get_computer_move()
print 'move white:', move_white

sys.exit(1)



black = Chess()
white = Chess()
white.child.expect ('Your move is')
white.switch()

move_white = white.get_first_computer_move()
print 'first move white:', move_white

black.do_first_move (move_white)
move_black = black.get_first_computer_move()
print 'first move black:', move_black

white.do_move (move_black)

done = 0
while not done:
    move_white = white.get_computer_move()
    print 'move white:', move_white

    black.do_move (move_white)
    move_black = black.get_computer_move()
    print 'move black:', move_black
   
    white.do_move (move_black)
    print 'tail of loop'

g.quit()


