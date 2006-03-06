#!/usr/bin/env python
import socket
import sys, time, select

def recv_wrapper(s):
    r,w,e = select.select([s.fileno()],[],[], 2)
    if not r:
        return ''
    cols = int(s.recv(4))
    rows = int(s.recv(4))
    packet_size = cols * rows 
    return s.recv(packet_size)

HOST = '' #'localhost'    # The remote host
PORT = 1664 # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
time.sleep(1)
#s.setblocking(0)
s.send('COMMAND' + '\x01' + sys.argv[1])
print recv_wrapper(s)
s.close()
sys.exit()
#while True:
#    data = recv_wrapper(s)
#    if data == '':
#        break
#    sys.stdout.write (data)
#    sys.stdout.flush()
#s.close()

