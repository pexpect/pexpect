#!/usr/bin/env python
'''This module implements a Finite State Machine (FSM) with one stack.
The FSM is fairly simple. It is useful for small parsing tasks.
The addition of a stack makes it much simpler to build tiny parsers.

The FSM is an association of
    (input_symbol, current_state) --> (action, next_state)
When the FSM matches the pair (input_symbol, current_state)
it will call the associated action and then set the next state.
The action will be passed input_symbol, current state, and a stack.
'''

class ANY:
    '''This is a meta key. This is a class, but you use it like a value.
    Example: x = ANY
    Example: f.add_transaction (ANY, 'SOMESTATE', None, 'OTHERSTATE')
    '''
    pass

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

    def add_default_transition (self, action, next_state):
        '''This sets the default transition.
        If the FSM cannot match the pair (input_symbol, current_state)
        in the transition table then this is the transition that 
        will be returned. This is useful for catching errors and undefined states.
        The default transition can be removed by calling
        add_default_transition (None, None)
        If the default is not set and the FSM cannot match
        the input_symbol and current_state then it will 
        raise an exception (see process()).
        '''
        if action == None and next_state == None:
            self.default_transition = None
        else:
            self.default_transition = (action, next_state)

    def add_transition (self, input_symbol, state, action, next_state):
        '''This adds an association between inputs and outputs.
                (input_symbol, current_state) --> (action, next_state)
           The action may be set to None.
           The input_symbol may be set to None.
        '''
        self.state_transitions[(input_symbol, state)] = (action, next_state)

    def add_transition_list (self, list_input_symbols, state, action, next_state):
        '''This adds lots of the same transitions for different input symbols.
        You can pass a list or a string. Don't forget that it is handy to use
        string.digits, string.letters, etc. to add transitions that match 
        those character classes.
        '''
        for input_symbol in list_input_symbols:
            self.add_transition (input_symbol, state, action, next_state)

    def get_transition (self, input_symbol, state):
        '''This tells what the next state and action would be 
        given the current state and the input_symbol.
        This returns (action, new state).
        This does not update the current state
        nor does it trigger the output action.
        If the transition is not defined and the default state is defined
        then that will be used; otherwise, this throws an exception.
        '''
        if self.state_transitions.has_key((input_symbol, self.current_state)):
            return self.state_transitions[(input_symbol, self.current_state)]
        elif self.state_transitions.has_key ((ANY, self.current_state)):
            return self.state_transitions[(ANY, self.current_state)]
        elif self.default_transition != None:
            return self.default_transition
        else:
            raise Exception ('Transition is undefined.')
        
    def process (self, input_symbol):
        '''This causes the fsm to change state and call an action.
        (input_symbol, current_state) --> (action, next_state)
        If the action is None then the action is not called and
        only the current state is changed.
        '''
        (action, next_state) = self.get_transition (input_symbol, self.current_state)
        if action != None:
            apply (action, (input_symbol, self) )
        self.current_state = next_state

    def process_string (self, s):
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
def Error (input_symbol, fsm):
    print 'UNDEFINED: %s, %s -- RESETTING' % (input_symbol, fsm.state)
    fsm.reset()
def StartBuildTag (input_symbol, fsm):
    fsm.push (input_symbol)
def BuildTag (input_symbol, fsm):
    s = fsm.pop ()
    s = s + input_symbol
    fsm.push (s)
def DoneBuildTag (input_symbol, fsm):
    pass
def DoneEmptyElement (input_symbol, fsm):
    s = fsm.pop()
    print s
def StartBuildEndTag (input_symbol, fsm):
    fsm.push (input_symbol)
def BuildEndTag (input_symbol, fsm):
    s = fsm.pop ()
    s = s + input_symbol
    fsm.push (s)
def DoneBuildEndTag (input_symbol, fsm):
    s1 = fsm.pop ()
    s2 = fsm.pop ()
    if s1 == s2:
        print s1
    else:
        print 'Not valid XML.'

def test():
    f = FSM('INIT')
    f.add_default_transition (Error, 'INIT')
    f.add_transition ('<', 'INIT', None, 'TAG')
    f.add_transition (ANY, 'INIT', None, 'INIT') # Ignore white space between tags

    f.add_transition ('?', 'TAG', None, 'XML_DECLARATION')
    f.add_transition (ANY, 'XML_DECLARATION', None, 'XML_DECLARATION')
    f.add_transition ('?', 'XML_DECLARATION', None, 'XML_DECLARATION_END')
    f.add_transition ('>', 'XML_DECLARATION_END', None, 'INIT')

    # Handle building tags
    f.add_transition (ANY, 'TAG', StartBuildTag, 'BUILD_TAG')
    f.add_transition (ANY, 'BUILD_TAG', BuildTag, 'BUILD_TAG')
    f.add_transition (' ', 'BUILD_TAG', None, 'ELEMENT_PARAMETERS')
    f.add_transition ('/', 'TAG', None, 'END_TAG')
    f.add_transition ('/', 'BUILD_TAG', None, 'EMPTY_ELEMENT')
    f.add_transition ('>', 'BUILD_TAG', DoneBuildTag, 'INIT')

    # Handle element parameters
    f.add_transition ('>', 'ELEMENT_PARAMETERS', DoneBuildTag, 'INIT')
    f.add_transition ('/', 'ELEMENT_PARAMETERS', None, 'EMPTY_ELEMENT')
    f.add_transition ('"', 'ELEMENT_PARAMETERS', None, 'DOUBLE_QUOTE')
    f.add_transition (ANY, 'ELEMENT_PARAMETERS', None, 'ELEMENT_PARAMETERS')

    # Handle quoting inside of parameter lists
    f.add_transition (ANY, 'DOUBLE_QUOTE', None, 'DOUBLE_QUOTE')
    f.add_transition ('"', 'DOUBLE_QUOTE', None, 'ELEMENT_PARAMETERS')

    # Handle empty element tags
    f.add_transition ('>', 'EMPTY_ELEMENT', DoneEmptyElement, 'INIT')

    # Handle end tags
    f.add_transition (ANY, 'END_TAG', StartBuildEndTag, 'BUILD_END_TAG')
    f.add_transition (ANY, 'BUILD_END_TAG', BuildEndTag, 'BUILD_END_TAG')
    f.add_transition ('>', 'BUILD_END_TAG', DoneBuildEndTag, 'INIT')

    f.process_string (XML_TEST_DATA)
    
    if len(f.stack) == 0:
        print 'XML file is valid.'
    else:
        print 'XML file is not valid. Stack is not empty.'
        print f.stack

if __name__ == '__main__':
    test ()
