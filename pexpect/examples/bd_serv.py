#!/usr/bin/env python
import socket, pexpect
import time

p = pexpect.spawn ('bash')
time.sleep (0.1)
p.expect ('\$')
time.sleep (0.1)

HOST = ''                 # Symbolic name meaning the local host
PORT = 1666               # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
print 'Listen'
s.listen(1)
print 'Accept'
while 1:
    conn, addr = s.accept()
    print 'Connected by', addr
    data = conn.recv(1024)
    print 'RECEIVED:'
    print data
#    if not data:
#        break
    time.sleep (0.1)
    p.sendline (data)
    time.sleep (0.1)
    p.expect ('\$')
    time.sleep (0.1)
    response = p.before + p.after
    print 'RESPONSE:'
    print response
    conn.send(response)
    
conn.close()

