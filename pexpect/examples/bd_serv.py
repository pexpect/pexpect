#!/usr/bin/env python
import socket, pexpect

p = pexpect.spawn ('bash')
p.expect ('# ')

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
#    if not data:
#        break
    p.sendline (data)
    p.expect ('# ')
    response = p.before + p.after
    conn.send(response)
    
conn.close()

