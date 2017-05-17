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
    command = raw_input('>> ')
    raw_command = command.split()[0]
	
    control_socket.send(raw_command.encode())

    if raw_command == 'LIST':
		result = control_socket.recv(2048)
		print result

    if raw_command == 'RETR':
		file_name = command.split()[1]
		control_socket.send(file_name.encode())
		result = data_socket.recv(65536)
		print result
		file = open(path + file_name, 'wb+')
		file.write(result)
		file.close