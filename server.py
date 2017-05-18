import socket
import os
import time
from threading import Thread
from socketserver import ThreadingMixIn


data_port = 3020
control_port = 3021
server = '172.24.36.112'
print(server)
path = 'files/'


class ClientThread(Thread):

    def __init__(self, control_conn, data_conn, IP):
        Thread.__init__(self)
        self.IP = IP
        self.data_conn = data_conn
        self.control_conn = control_conn
        # self.web_socket = web_socket

        print("[+] New client connected " + IP)

    def recvall(self, size):
        "start recv"
        data = bytes()
        while len(data) < size:
            packet = self.web_socket.recv(size - len(data))
            if not packet:
                return None
            data += packet
            print(len(data))

        return data

    def get_from_server(self, file_name):

        host = socket.gethostbyname('ceit.aut.ac.ir')
        print(host)

        URL_head = "HEAD /~94131090/CN1_Project_Files/"   + str(file_name) + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
        URL_get = "GET /~94131090/CN1_Project_Files/" + str(file_name) + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
        web_socket = socket.socket(socket.AF_INET, socket.SOL_SOCKET)
        self.web_socket = web_socket
        self.web_socket.connect((host, 80))
        self.web_socket.send(URL_head.encode())
        result = self.web_socket.recv(4096).decode()
        # print(result)
        http_status = result[9:12]
        print("status code: " + http_status)
        tmp = result.encode()

        if http_status == '200':
            size_i = result.find('Content-Length')+16
            index = 0
            while True:
                if tmp[size_i + index] == 13:
                    break
                index += 1
            print(str(index))
            size = int(result[size_i:size_i + index])
            while True:
                if tmp[index] == 13 and tmp[index+3] == 10:
                    head_size = index + 4
                    break
                index += 1

            size = size + head_size


            self.web_socket.send(URL_get.encode())
            data = self.recvall(size)


            file = open(path + str(file_name), 'wb+')
            file.write(data[head_size:size])
            file.close()

        web_socket.close()


    def send_file(self, file_name):
        files = os.listdir(path)

        #send local
        for file in files:
            if file_name == file:
                file = open(path + file_name, 'rb')
                if file != "":
                    data = file.read(65536)
                    code = 150
                    self.control_conn.send(str(code).encode())
                    time.sleep(1)
                    self.control_conn.send(str(len(data)).encode())
                    self.data_conn.send(data)
                else:
                    code = 550
                    self.control_conn.sendall(code.encode())
                return

        # send remote
        self.get_from_server(file_name)
        try:
            file = open(path + file_name, 'rb')
            code = 150
        except:
            code = 550

        if code == 150:
            data = file.read(65536)
            self.control_conn.send(str(code).encode())
            time.sleep(1)
            self.control_conn.send(str(len(data)).encode())
            self.data_conn.send(data)
            print("file " + file_name + " downloaded by client " + self.IP)

        elif code == 550:
            self.control_conn.send(str(code).encode())


    def do_command(self, command):
        raw_command = command.split()[0]
        if raw_command == 'LIST':
            files = os.listdir(path)
            #list files from server

        if raw_command == 'RETR':
            file_name = command.split()[1]
            self.send_file(file_name)


    def run(self):
        while True:
            command = self.control_conn.recv(1024).decode()
            self.do_command(command)

#data socket
data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
data_socket.bind((server, data_port))

#control socket
control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
control_socket.bind((server, control_port))

#web server socket


threads = []
data_socket.listen(10)
control_socket.listen(10)

control_conns = []
data_conns = []
IPs = []
D_PORTs = []
C_PORTs = []

i=0

print("waiting for connections !")

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
