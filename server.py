import socket
import os
import time
import datetime
from threading import Thread
from socketserver import ThreadingMixIn


data_port = 3020
control_port = 3021
server = '172.24.36.134'
print(server)
path = 'files/'


class ClientThread(Thread):

    def __init__(self, control_conn, data_conn, IP):
        Thread.__init__(self)
        self.IP = IP
        self.data_conn = data_conn
        self.control_conn = control_conn
        self.files_list = []
        self.files = ""
        log_file = open('logs/server-logs.txt', 'a+')
        log_file.write("client " + self.IP + " connected at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        log_file.close()

        print("[+] New client connected " + IP)

    def recvall(self, size):

        data = bytes()
        while len(data) < size:
            packet = self.web_socket.recv(size - len(data))
            if not packet:
                return None
            data += packet

        return data


    def get_size(self, result):
        tmp = result.encode()
        size_i = result.find('Content-Length')+16
        index = 0
        while True:
            if tmp[size_i + index] == 13:
                break
            index += 1

        size = int(result[size_i:size_i + index])
        while True:
            if tmp[index] == 13 and tmp[index+3] == 10:
                head_size = index + 4
                break
            index += 1

        size = size + head_size
        return size, head_size

    def get_from_server(self, file_name):

        host = socket.gethostbyname('ceit.aut.ac.ir')
        print(host)
        file_name = file_name.replace(" ", "%20")
        URL_head = "HEAD /~94131090/CN1_Project_Files/" + str(file_name) + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
        URL_get = "GET /~94131090/CN1_Project_Files/" + str(file_name) + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
        web_socket = socket.socket(socket.AF_INET, socket.SOL_SOCKET)
        self.web_socket = web_socket
        self.web_socket.connect((host, 80))
        self.web_socket.send(URL_head.encode())
        result = self.web_socket.recv(4096).decode()
        http_status = result[9:12]
        print("status code: " + http_status)
        tmp = result.encode()
        data = bytes()
        if http_status == '200':

            (size, head_size) = self.get_size(result)
            self.web_socket.send(URL_get.encode())
            data = self.recvall(size)
            file_name = file_name.replace('%20', ' ')
            file = open(path + str(file_name), 'wb+')
            file.write(data[head_size:size])    
            file.close()

        web_socket.close()
        return data

    def list_files(self):
        host = socket.gethostbyname('ceit.aut.ac.ir')

        URL_head = "HEAD /~94131090/CN1_Project_Files/ HTTP/1.1\r\nHost:\r\n\r\n"
        URL_get = "GET /~94131090/CN1_Project_Files/ HTTP/1.1\r\nHost:\r\n\r\n"
        web_socket = socket.socket(socket.AF_INET, socket.SOL_SOCKET)
        self.web_socket = web_socket
        self.web_socket.connect((host, 80))
        self.web_socket.send(URL_get.encode())
        result = self.web_socket.recv(4096).decode()
        http_status = result[9:12]

        if http_status == '200':
            i = 0
            (size, head_size) = self.get_size(result)
            self.web_socket.send(URL_get.encode())
            result = self.recvall(size).decode()
            tmp = result

            index = tmp.find('HTTP')
            tmp = tmp[index:len(tmp)] + tmp[:index]
            index = 0
            while index != -1:
                index = tmp.find('<a ')
                i += 1
                tmp = tmp[index+2:len(tmp)]
                s_index = tmp.find('>') + 1
                e_index = tmp.find('</a>')
                self.files_list.append(tmp[s_index:e_index])

            self.files_list.remove('Name')
            self.files_list.remove('Last modified')
            self.files_list.remove('Size')
            self.files_list.remove('Description')
            self.files_list.remove('Parent Directory')
            self.files_list.pop()

            for file in self.files_list:
                self.files = self.files + "\n" + file


            self.control_conn.send(str(len(self.files)).encode())
            self.data_conn.send(self.files.encode())

            self.files = ""
            self.files_list = []
        

    def send_file(self, file_name):
        files = os.listdir(path)

        #send local
        for file in files:
            if file_name == file:
                file = open(path + file_name, 'rb')
                if file != "":
                    data = file.read()
                    code = 150
                    self.control_conn.send(str(code).encode())
                    time.sleep(1)
                    self.control_conn.send(str(len(data)).encode())
                    self.data_conn.send(data)
                    log_file = open('logs/server-logs.txt', 'a+')
                    log_file.write(file_name + " downloaded by " + self.IP + "\n")
                    log_file.close()
                else:
                    code = 550
                    self.control_conn.send(code.encode())
                return

        # send remote
        data = self.get_from_server(file_name)

        if len(data) > 0:
            code = 150
        else:
            code = 550

        if code == 150:
            file = open(path + file_name, 'rb')
            data = file.read()
            self.control_conn.send(str(code).encode())
            time.sleep(1)
            self.control_conn.send(str(len(data)).encode())
            self.data_conn.send(data)
            log_file = open('logs/server-logs.txt', 'a+')
            log_file.write("file " + file_name + " downloaded by client " + self.IP + "\n")
            log_file.close()

        elif code == 550:
            self.control_conn.send(str(code).encode())


    def do_command(self, command):
        raw_command = command.split()[0]
        
        if len(command.split()) > 1:
            index = command.find(' ')
            file_name = command[index+1:len(command)]
        
        if raw_command == 'LIST':
            self.list_files()

        if raw_command == 'RETR':
            print(file_name)
            self.send_file(file_name)


    def run(self):
        print("run")
        username = self.control_conn.recv(1024).decode()
        time.sleep(0.3)
        password = self.control_conn.recv(1024).decode()
        if (username == "root") and (password == "toor"):
            print("authed")
            self.control_conn.send("authed".encode())
            while True:
                command = self.control_conn.recv(1024).decode()
                self.do_command(command)
        else:
            print("unauthed")
            self.control_conn.send("unauthed".encode())

#data socket
data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
data_socket.bind((server, data_port))

#control socket
control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
control_socket.bind((server, control_port))

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
