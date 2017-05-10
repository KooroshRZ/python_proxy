import socket
import os
import glob

def handle(command):
    if command == 'LIST':
        files = os.listdir(path)
        for file in files:
            c.send(file.encode())


ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '172.24.34.110'
port = 3000
ss.bind((host, port))

ss.listen(5)
c, addr = ss.accept()
print 'connection from ', addr
c.send('thnx for connecting')


path = 'files/'
while True:
    command = c.recv(1024)
    handle(command)
