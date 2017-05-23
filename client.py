import socket
import time

path = 'client_files/'

data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '192.168.139.233'
data_port = 3020
control_port = 3021

control_socket.connect((host, control_port))
data_socket.connect((host, data_port))

def recvall(size, data_socket):
    data = bytes()
    while len(data) < size:
        packet = data_socket.recv(size - len(data))
        if not packet:
            return None
        data += packet


    return data

username = input('Username: ')
password = input('Password: ')

control_socket.send(username.encode())
time.sleep(0.3)
control_socket.send(password.encode())

auth = control_socket.recv(1024).decode()
print(auth)
if auth == "authed":
    print("authenticated successfull !!")
    while True:    
        command = input('\n>> ')

        raw_command = command.split()[0]
        control_socket.send(command.encode())

        if raw_command == 'QUIT':
            break

        elif raw_command == 'LIST':
            size = control_socket.recv(1024).decode()
            result = recvall(int(size), data_socket)
            print(result.decode())

        elif raw_command == 'RETR':

            index = command.find(' ')
            file_name = command[index+1:len(command)]
            code = control_socket.recv(1024).decode()

            if code == '150':
                size = control_socket.recv(1024).decode()
                data = recvall(int(size), data_socket)
                file = open(path + file_name, 'wb+')
                file.write(data)
                file.close()
                print("file downloaded successfully!")
            elif code == '550':
                print("file not found or access denied !!!")

        elif raw_command == 'DELE':

            index = command.find(' ')
            file_name = command[index+1:len(command)]
            code = control_socket.recv(1024).decode()
            if code == '150':
                print("file" + file_name + " deleted successfully")
            elif code == '550':
                print("No such file !!")

        elif raw_command == 'RMD':
            code = control_socket.recv(1024).decode()
            if code == '150':
                print("cache cleared !!")
            elif code == '550':
                print("cache is empty !!")
else:
    print("Not authenticated !")