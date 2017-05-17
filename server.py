import socket
import os
# import glob
from threading import Thread
from SocketServer import ThreadingMixIn


data_port = 3020
control_port = 3021
host = '172.24.36.112'
path = 'files/'

class ClientThread(Thread):

    def __init__(self, control_conn, data_conn, IP, PORT):
        Thread.__init__(self)
        self.IP = IP
        self.PORT = PORT
        self.data_conn = data_conn
        self.control_conn = control_conn
        print "[+] New server socket thread started for " + IP + ":" + str(PORT)

    def do_command(self, command):
        if command == "LIST":
            files = os.listdir(path)
            for file in files:
                control_conn.send(file.encode())
                control_conn.send("\n".encode())
        if command == "RETR":
            file_name = control_conn.recv(1024)
            print "file name : " ,file_name
            file = open(path + file_name, 'r')
            result = file.read(1000)
            data_conn.send(result.encode())


    def run(self):
        while True:
            command = self.control_conn.recv(1024)
            self.do_command(command)
	    


data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
data_socket.bind((host, data_port))

control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
control_socket.bind((host, control_port))

threads = []
# control_threads = []
data_socket.listen(10)
control_socket.listen(10)

while True:
    print "Multithreded Python server : waiting for connections from clients"
    (data_conn, (IP, PORT)) = data_socket.accept()
    (control_conn, (IP, PORT)) = control_socket.accept()

    new_thread = ClientThread(control_conn, data_conn, IP, PORT)
    new_thread.start()
    threads.append(new_thread)

    # new_thread = ClientThread(conn, IP, PORT)
    # new_thread.start()
    # control_threads.append(new_thread)

for t in threads:
    t.join()