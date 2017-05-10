import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '172.24.34.110'
port = 3000

s.connect((host, port))
recieved = s.recv(1024)
print recieved

if recieved != "":
    while True:
        command = raw_input('>> ')
        s.send(command.encode())
        if (command == 'LIST'):
            result = s.recv(1024)
            print result
s.close()
