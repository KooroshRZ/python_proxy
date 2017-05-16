import socket

data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '172.24.36.112'
data_port = 3020
control_port = 3021

control_socket.connect((host, control_port))
data_socket.connect((host, data_port))

recieved = data_socket.recv(1024)
print recieved

# if recieved != "":
    # while True:
    #     # command = raw_input('>> ')
    #     # # s.send(command.encode())
    #     # if (command == 'LIST'):
    #     #     result = s.recv(1024)
    # s.close()
    #         print result
