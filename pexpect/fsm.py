#!/usr/bin/env python
'''This module implements a Finite State Machine (FSM) with one stack.
The addition of a stack makes it much simpler to build tiny parsers.
The FSM is fairly simple. It is useful for small parsing tasks.

This FSM is defined by an association of
    (input_symbol, current_state) --> (action, next_state)
You can also define a association of 
                  (current_state) --> (action, next_state)
Which is check if no (input_symbol, current_state) matches.
Finally, if none of these match then the FSM checks to see
if the default transition has been set. If this has been
set that that action is called and state is set.

When the FSM matches the pair (input_symbol, current_state)
it will call the associated function "action" and then set the next state.
The action will be passed input_symbol, and the FSM.
You can use None for an action in which case this class
behaves just like a simple Finite State Machine where only the
next state is set.

Noah Spurrier 20020814
'''

class ExceptionFSM(Exception):
    '''Base class for all exceptions raised by this module.'''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return `self.value`

class FSM:
    '''This class is a Finite State Machine (FSM) with one stack.
    You set up a state transition table which is
    The FSM is an association of
        (input_symbol, current_state) --> (action, next_state)
    When the FSM matches a pair (current_state, input_symbol)
    it will call the associated action
    The action is a function reference defined with a signature like this:
            def a (input_symbol, fsm):
    and pass as parameters the current state, the input symbold, and a stack.
    As an additional aid a stack is given.
    The stack is really just a list.
    The action function may produce output and update the stack.
    '''  

    def __init__(self, initial_state = None):
        self.state_transitions = {}   # Map (input_symbol, state) to (action, next_state).
        self.state_transitions_any = {} # Map (state) to (action, next_state).
        self.default_transition = None
        self.initial_state = initial_state
        self.current_state = self.initial_state
        self.stack = []

    def push (self, v):
        '''This pushes a value onto the stack.'''
        self.stack.append (v)
    def pop (self):
        '''This pops a value off the stack and returns the value.'''
        return self.stack.pop ()
        
    def reset (self):
        '''This clears the stack and resets the current_state to the initial_state.
        '''
        self.current_state = self.initial_state
        self.stack = []

    def set_default_transition (self, action, next_state):
        '''This sets the default transition. This is the action and state
        that is set if the FSM cannot find the input_symbol and the
        current_state.

        This is useful for catching errors and undefined states.
        The default transition can be removed by calling
        set_default_transition (None, None)
        If the default is not set and the FSM cannot match
        the input_symbol and current_state then it will 
        raise an exception (see process()).        

        See also add_transition_any()
        '''
        if action == None and next_state == None:
            self.default_transition = None
        else:
            self.default_transition = (action, next_state)

    def add_transition (self, input_symbol, state, action, next_state):
        '''This adds an association between 
                (input_symbol, current_state) --> (action, next_state)
           The action may be set to None.
           
           You can also set transitions for a set of symbols by using
           add_transition_list().
        '''
        self.state_transitions[(input_symbol, state)] = (action, next_state)

    def add_transition_list (self, list_input_symbols, state, action, next_state):
        '''This adds lots of the same transitions for different input symbols.
        You can pass a list or a string. Don't forget that it is handy to use
        string.digits, string.whitespace, string.letters, etc. to add transitions 
        that match character classes.
        '''
        for input_symbol in list_input_symbols:
            self.add_transition (input_symbol, state, action, next_state)

    def add_transition_any (self, state, action, next_state):
        '''This adds an association between any input_symbol
        The process() method check these transitions after the
        transitions that match a specific input symbol. The effect
        is that these transitions match any input_symbol and a
        specific current state.
        '''
        self.state_transitions_any [state] = (action, next_state)

    def get_transition (self, input_symbol, state):
        '''This tells what the next state and action would be 
        given the current state and the input_symbol.
        This returns (action, new state).
        This does not update the current state
        nor does it trigger the output action.
        
        There are three steps in the sequence of checking for a defined transition.
        This goes in order from the most specific to the least specific.
        
        1. First check state_transitions[] that match (input_symbol, current_state)
        2. Second check state_transitions_any that match (current_state)
           The effect is that any input_symbol that didn't match as part of
           a state_transition[] will match if the state is defined here.
        3. Third check if the default_transition is defined.
           This matches any input_symbol and any state.
           Theis is the handler for any error, undefined state, or defaults
           that you want. Everything goes here if on handled by 1. or 2.
        4. If the no transition is defined then raise an exception.
        '''
        if self.state_transitions.has_key((input_symbol, self.current_state)):
            return self.state_transitions[(input_symbol, self.current_state)]
        elif self.state_transitions_any.has_key (self.current_state):
            return self.state_transitions_any[self.current_state]
        elif self.default_transition != None:
            return self.default_transition
        else:
            raise ExceptionFSM ('Transition is undefined.')
        
    def process (self, input_symbol):
        '''This is the main method you call to process input.
        This causes the FSM to change state and call an action.
            (input_symbol, current_state) --> (action, next_state)
        If the action is None then the action is not called and
        only the current state is changed.
        '''
        (action, next_state) = self.get_transition (input_symbol, self.current_state)
        if action != None:
            apply (action, (input_symbol, self) )
        self.current_state = next_state

    def process_string (self, s):
    	'''This takes each character of the string and sends it to process().
    	'''
        for c in s:
            self.process (c)

        
###################################################################
# The following is a test of the FSM
#
# This is not a real XML validator. It ignores character sets,
# entity and character references, and attributes.
# But it does check the tree structure and
# can tell if the XML input is generally well formed or not.
####################################################################
#http://www.w3.org/TR/REC-xml#NT-Name
import string
XML_TEST_DATA = '''<?xml version="1.0"?>
<graph>
  <att name="directed" value="1" />
  <att name="mode" value="FA" />
  <att name="start" value="q0" />
    <node id="0" label="q0">
      <graphics x="-172.0" y="13.0" z="0.0" />
    </node>
    <node id="1" label="q1">
      <graphics type="hexagon"  x="10.0" y="74.0" z="-0.0"/>
    </node>
    <node id="2" label="q2" accept="1">
      <graphics x="169.0" y="-5.0" z="-0.0" />
    </node>
    <node id="3" label="q3" >
      <graphics x="19.0" y="8.0" z="-0.0" />
    </node>
    <node id="4" label="q4">
      <graphics  x="18.0" y="-74.0" z="-0.0" />
    </node>
    <edge source="0" target="1" label="ab"/>
    <edge source="1" target="2" label="aa"/>
    <edge source="2" target="2" label="c"/>
    <edge source="0" target="3" label="ba"/>
    <edge source="3" target="2" label="aa"/>
    <edge source="0" target="4" label="a"/>
    <edge source="4" target="2" label="c" />
    <edge source="2" target="4" label="ab" />
</graph>
'''
import sys

def emit (s):
    sys.stdout.write (s)
def Error (input_symbol, fsm):
    print 'UNDEFINED: %s, %s -- RESETTING' % (input_symbol, fsm.current_state)
    fsm.reset()
def Passthrough (input_symbol, fsm):
    emit (input_symbol)
def StartBuildTag (input_symbol, fsm):
    fsm.push (input_symbol)
    emit (input_symbol)
def BuildTag (input_symbol, fsm):
    s = fsm.pop ()
    s = s + input_symbol
    fsm.push (s)
    emit (input_symbol)
def DoneBuildTag (input_symbol, fsm):
    pass
    emit (input_symbol)
def DoneEmptyElement (input_symbol, fsm):
    s = fsm.pop()
    emit (input_symbol)
    
def StartBuildEndTag (input_symbol, fsm):
    fsm.push (input_symbol)
    emit (input_symbol)
def BuildEndTag (input_symbol, fsm):
    s = fsm.pop ()
    s = s + input_symbol
    fsm.push (s)
    emit (input_symbol)
def DoneBuildEndTag (input_symbol, fsm):
    s1 = fsm.pop ()
    s2 = fsm.pop ()
    if s1 != s2:
        print 'Not valid XML.'
    emit (input_symbol)

def demo ():
    f = FSM('INIT')
    
    f.set_default_transition (Error, 'INIT')
    
    f.add_transition ('<', 'INIT', Passthrough, 'TAG')
    f.add_transition_any ('INIT', Passthrough, 'INIT')

    f.add_transition ('?', 'TAG', Passthrough, 'XML_DECLARATION')
    f.add_transition_any ('XML_DECLARATION', Passthrough, 'XML_DECLARATION')
    f.add_transition ('?', 'XML_DECLARATION', Passthrough, 'XML_DECLARATION_END')
    f.add_transition ('>', 'XML_DECLARATION_END', Passthrough, 'INIT')

    # Handle building tags
    f.add_transition_any ('TAG', StartBuildTag, 'BUILD_TAG')
    f.add_transition_any ('BUILD_TAG', BuildTag, 'BUILD_TAG')
    f.add_transition_list (string.whitespace, 'BUILD_TAG', Passthrough, 'ELEMENT_PARAMETERS')
    f.add_transition ('/', 'TAG', Passthrough, 'END_TAG')
    f.add_transition ('/', 'BUILD_TAG', Passthrough, 'EMPTY_ELEMENT')
    f.add_transition ('>', 'BUILD_TAG', DoneBuildTag, 'INIT')

    # Handle element parameters
    f.add_transition ('>', 'ELEMENT_PARAMETERS', DoneBuildTag, 'INIT')
    f.add_transition ('/', 'ELEMENT_PARAMETERS', Passthrough, 'EMPTY_ELEMENT')
    f.add_transition ('"', 'ELEMENT_PARAMETERS', Passthrough, 'DOUBLE_QUOTE')
    f.add_transition_any ('ELEMENT_PARAMETERS', Passthrough, 'ELEMENT_PARAMETERS')

    # Handle quoting inside of parameter lists
    f.add_transition_any ('DOUBLE_QUOTE', Passthrough, 'DOUBLE_QUOTE')
    f.add_transition ('"', 'DOUBLE_QUOTE', Passthrough, 'ELEMENT_PARAMETERS')

    # Handle empty element tags
    f.add_transition ('>', 'EMPTY_ELEMENT', DoneEmptyElement, 'INIT')

    # Handle end tags
    f.add_transition_any ('END_TAG', StartBuildEndTag, 'BUILD_END_TAG')
    f.add_transition_any ('BUILD_END_TAG', BuildEndTag, 'BUILD_END_TAG')
    f.add_transition ('>', 'BUILD_END_TAG', DoneBuildEndTag, 'INIT')

    f.process_string (XML_TEST_DATA)
    
    print
    if len(f.stack) == 0:
        print 'XML file is valid.'
    else:
        print 'XML file is not valid. Stack is not empty.'
        print f.stack

if __name__ == '__main__':
    '''Finite State Machine and push-down Automata (FSM and PDA)
    
    Here is a simple little Finite State Machine. It includes a stack. 
    This is useful for little parsing tasks. Included is a test which
    reformats XML code.
    '''
    demo ()
