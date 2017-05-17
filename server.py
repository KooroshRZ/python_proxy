import socket
import select
import os
# import glob
from threading import Thread
from socketserver import ThreadingMixIn


data_port = 3020
control_port = 3021
host = '172.24.36.112'
path = 'files/'


class ClientThread(Thread):

    def __init__(self, control_conn, data_conn, IP):
        Thread.__init__(self)
        self.IP = IP
        self.data_conn = data_conn
        self.control_conn = control_conn
        print("[+] New client connected " + IP)

    def do_command(self, command):
        
        if command == 'LIST':
            files = os.listdir(path)
            for file in files:
                self.control_conn.sendall(file.encode())
                self.control_conn.sendall("\n".encode())
                
        if command == 'RETR':
            file_name = self.control_conn.recv(4096).decode()
            print("file name" + file_name)
            file = open(path + file_name, 'r')
            result = file.read(1000)
            self.data_conn.sendall(result.encode())

    def run(self):
        while True:
            command = self.control_conn.recv(4096).decode()
            self.do_command(command)
	    

data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
data_socket.bind((host, data_port))

control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
control_socket.bind((host, control_port))

threads = []
data_socket.listen(10)
control_socket.listen(10)

control_conns = []
data_conns = []
IPs = []
D_PORTs = []
C_PORTs = []

i=0

while True:

    (data_conn, (IP, D_PORT)) = data_socket.accept()
    (control_conn, (IP, C_PORT)) = control_socket.accept()
    control_conns.append(control_conn)
    data_conns.append(data_conn)

    new_thread = ClientThread(control_conns[i], data_conns[i], IP)
    new_thread.start()
    threads.append(new_thread)
    i += 1


for t in threads:
    t.join()