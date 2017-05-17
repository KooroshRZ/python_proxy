import socket

path = 'client_files/'

data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '172.24.36.112'
data_port = 3020
control_port = 3021

control_socket.connect((host, control_port))
data_socket.connect((host, data_port))

#######################################################################################################
# web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# web_socket.connect(("192.168.128.30", 80))
# web_socket.sendall("GET /~94131090/CN1_Project_Files/flower.jpeg HTTP/1.1\r\nHost: 192.168.128.30\r\n\r\n".encode())
# result = web_socket.recv(65536)
# print(result)
# web_socket.close()
#
# # print("result: " + str(result))
# file = open('flower.jpeg', 'wb+')
# file.write(result)
# file.close()
######################################################################################################

def recvall(size, data_socket):
    data = bytes()
    while len(data) < size:
        packet = data_socket.recv(size - len(data))
        if not packet:
            return None
        data += packet

    return data


while True:
    command = input('>> ')
    raw_command = command.split()[0]
    control_socket.send(command.encode())

    if raw_command == 'QUIT':
    	break

    elif raw_command == 'LIST':
        result = control_socket.recv(4096).decode()
        print(result)

    elif raw_command == 'RETR':

        file_name = command.split()[1]
        code = control_socket.recv(1024).decode()

        
        if code == '150':
        	size = control_socket.recv(1024).decode()
	        data = recvall(int(size), data_socket)
	        file = open(path + file_name, 'wb+')
	        file.write(data)
	        file.close()
	        print("file downloaded successfully!")
        elif code == '550':
        	print("file not found")

