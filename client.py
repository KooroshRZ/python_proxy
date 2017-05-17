import socket

path = 'client_files/'

data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '172.24.36.112'
data_port = 3020
control_port = 3021

control_socket.connect((host, control_port))
data_socket.connect((host, data_port))

while True:

    command = input('>> ')
    raw_command = command.split()[0]
    control_socket.sendall(raw_command.encode())

    if raw_command == 'QUIT':
    	break

    elif raw_command == 'LIST':
        result = control_socket.recv(4096).decode()
        print(result)

    elif raw_command == 'RETR':
        file_name = command.split()[1]
        control_socket.sendall(file_name.encode())
        result = data_socket.recv(4096).decode()
        file = open(path + file_name, 'wb+')
        file.write(result.encode())
        file.close()