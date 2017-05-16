import socket
# import os
# import glob
from threading import Thread
from SocketServer import ThreadingMixIn

class ClientThread(Thread):
    def __init__(self, conn, IP, PORT):
        Thread.__init__(self)
        self.IP = IP
        self.PORT = PORT
        self.conn = conn
        print "[+] New server socket thread started for " + IP + ":" + str(PORT)
    def run(self):
        while True:
            command = conn.recv(2048)
            print "Server received data:", data
            MESSAGE = raw_input("Multithreaded Python server : Enter Response from Server/Enter exit:")
            if MESSAGE == 'exit':
                break
            conn.send(MESSAGE)
            #implement commands

# def handle(command):
#     if command == 'LIST':
#         files = os.listdir(path)
#         for file in files:
#             c.send(file.encode())

data_port = 3020
control_port = 3021
host = '172.24.36.112'
path = 'files/'


data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
data_socket.bind((host, data_port))

control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
control_socket.bind((host, control_port))

data_threads = []
control_threads = []
data_socket.listen(10)
control_socket.listen(10)

while True:
    print "Multithreded Python server : waiting for connections from clients"
    (conn, (IP, PORT)) = data_socket.accept()
    new_thread = ClientThread(conn, IP, PORT)
    new_thread.start()
    data_threads.append(new_thread)

    (conn, (IP, PORT)) = control_socket.accept()
    new_thread = ClientThread(conn, IP, PORT)
    new_thread.start()
    control_threads.append(new_thread)

for t in threads:
    t.join()
