import socket
from getpass import getpass
import time

class FTP:
    def __init__(self):
        self.isConnect = False
        self.connectedServer = None
        self.username = None
        self.password = None
        self.type = "Binary"
        self.valid_command = ('quit','bye','pwd','ascii','binary','open','disconnect','close','ls','get',
                              'put','delete','rename','user', 'cd')
        
    def receive_all(self,socket):
        all_data = b''
        while True:
            data = socket.recv(4096)
            all_data += data
            print(data.decode().rstrip())
            if not data:
                break
            elif len(data) < 4096:
                data_list = [d for d in data.split(b'\r\n') if d != b'']
                
                if len(data_list[-1]) >= 4:
                    last_resp = data_list[-1].decode()
                    if last_resp[0:3].isnumeric() and last_resp[3] == ' ':
                        break
                else:
                    break
                
        return all_data

    def recv_data(self,socket):
        all_data = b''
        while True:
            data = socket.recv(4096)
            all_data += data
            if not data:
                break
            
        return all_data
            
            
    def ext_code(self,resp):
        respone = resp.split()[0]
        return respone
    
    def user(self,username='',password=''):
        if username == '':
            username = input(f'Username ')
            if username == '':
                print('Usage: user username [password] [account]')
                return
        self.clientSocket.send(f'USER {username}\r\n'.encode())
        resp = self.clientSocket.recv(1024)
        print(resp.decode().rstrip())
        if password == '':
            password = getpass('Password: ')
            print('')
        
        self.clientSocket.send(f'PASS {password}\r\n'.encode())
        resp = self.receive_all(self.clientSocket)
        
        if resp.decode().startswith('5'):
            print('Login failed.')
            
    def req_user(self):
        code = ''
        self.username = input(f'User ({self.connectedServer}:(none)): ')
        self.clientSocket.send(f'USER {self.username}\r\n'.encode())
        resp = self.receive_all(self.clientSocket)
        if not (resp.startswith(b'5') or resp.startswith(b'4')):
            self.password = getpass('Password: ')
            print('')
            
            self.clientSocket.send(f'PASS {self.password}\r\n'.encode())
            resp = self.receive_all(self.clientSocket)
        
        if resp.decode().startswith('5'):
            print('Login failed.')
    
    def open(self,dest,port = 21):
        if not self.isConnect:
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.clientSocket.connect((dest, int(port)))
                resp = self.receive_all(self.clientSocket)
            except socket.gaierror:
                print(f"Unknown host {dest}.")
                return 
            except ConnectionRefusedError:
                print(f"> ftp: connect :Connection refused")
                return 
            except socket.error as msg:
                print(f"Failed to connect: {msg}")
                return 
            
            self.clientSocket.send('OPTS UTF8 ON\r\n'.encode())
            resp = self.receive_all(self.clientSocket)
            self.isConnect = True
            self.connectedServer = dest
            self.req_user()
        else:
            print(f'Already connected to {self.connectedServer}, use disconnect first.')
        
    def disconnect(self):
        if self.isConnect:
            self.set_default()
            self.clientSocket.send('QUIT\r\n'.encode())
            resp = self.clientSocket.recv(1024).decode()
            print(resp.rstrip())
            self.clientSocket.close()
        else:
            print('Not connected.')
            
    def quit(self):
        if self.isConnect:
            self.disconnect()
        print('')
    
    def ls(self,folder = ''):
        item_list = b''
        data_socket = self.get_data_socket()
        data_socket.listen()
        
        self.clientSocket.send(f'NLST {folder}\r\n'.encode())
        resp = self.receive_all(self.clientSocket)
        if resp.startswith(b'5') or resp.startswith(b'4'):
            return
        
        data_conn,data_addr = data_socket.accept()
        start_time = time.time()
        item_list = self.recv_data(data_conn)
        close_time = time.time()
        data_conn.close()
        
        print(item_list.decode().rstrip())
        resp = self.receive_all(self.clientSocket)
        if not (resp.startswith(b'5') and resp.startswith(b'4')):
            transfer_time = close_time - start_time
            if transfer_time == 0:
                transfer_time = 0.0001
            transfer_rate = (len(item_list)+3) / transfer_time / 1000
            print(f"ftp: {len(item_list)+3} bytes received in {transfer_time:.2f}Seconds {transfer_rate:.2f}Kbytes/sec.")
        
    def get(self,remote_file,local_file):
        file_data = b''
        data_socket = self.get_data_socket()
        data_socket.listen()
        
        start_time = time.time()
        self.clientSocket.send(f'RETR {remote_file}\r\n'.encode())
        resp = self.receive_all(self.clientSocket)
        
        if not (resp.startswith(b'5') or resp.startswith(b'4')):
            try:
                if self.type == "Binary":
                    file = open(local_file, "wb")
                else :
                    file = open(local_file, "w", encoding="utf-8")
            except FileNotFoundError:
                print("> R:No such process")
            except PermissionError:
                print(f"Error opening local file {local_file}.")
                return
            except Exception as msg:
                print(msg)
                return
            
            data_conn,data_addr = data_socket.accept()
            file_data = self.recv_data(data_conn)
            close_time = time.time()
            data_conn.close()
            resp = self.receive_all(self.clientSocket)
            
        if not (resp.startswith(b'5') or resp.startswith(b'4')):
            if self.type == "Ascii":
                file.write(file_data.decode('utf-8','replace'))
            else:
                file.write(file_data)
            file.close()
            transfer_time = close_time - start_time
            if transfer_time == 0:
                transfer_time = 0.0001
            transfer_rate = (len(file_data)) / transfer_time / 1000
            print(f"ftp: {len(file_data)} bytes received in {transfer_time:.2f}Seconds {transfer_rate:.2f}Kbytes/sec.")
        
    def put(self,local_file,remote_file):
        size = 0
        try:
            if self.type == "Binary":
                file = open(local_file, "rb")
            else :
                file = open(local_file, "r", encoding="utf-8")
        except FileNotFoundError:
            print(f"{local_file}: File not found")
            return
        except PermissionError:
            print(f"Error opening local file {local_file}.")
            return
        except Exception as msg:
            print(msg)
            return
        
        chunk = b''
        data_socket = self.get_data_socket()
        data_socket.listen()
        
        self.clientSocket.send(f'STOR {remote_file}\r\n'.encode())
        resp = self.receive_all(self.clientSocket)

        if not (resp.startswith(b'5') and resp.startswith(b'4')):
            start_time = time.time()
            data_conn,data_addr = data_socket.accept()
            while True:
                chunk = file.read(1024)
                if not chunk:
                    break
                size += len(chunk)
                data_conn.sendall(chunk)
            data_conn.close()
            close_time = time.time()
        file.close()
        
        resp = self.receive_all(self.clientSocket)
        if not (resp.startswith(b'5') and resp.startswith(b'4')):
            transfer_time = close_time - start_time
            if transfer_time == 0:
                transfer_time = 0.0001
            transfer_rate = size / transfer_time / 1000
            print(f"ftp: {size} bytes received in {transfer_time:.2f}Seconds {transfer_rate:.2f}Kbytes/sec.")
        
    def rename(self,old,new):
        self.clientSocket.send(f'RNFR {old}\r\n'.encode())
        resp = self.clientSocket.recv(1024).decode()
        print(resp.rstrip())
        if resp.startswith('5'):
            return
        self.clientSocket.send(f'RNTO {new}\r\n'.encode())
        resp = self.clientSocket.recv(1024).decode()
        print(resp.rstrip())
        
    def get_pasv_addr(self,reponse):
        temp = reponse.split()[4]
        parts = temp[1:-1].rstrip().split(',')
        ip = '.'.join(parts[:4])
        port = int(parts[4])*256 + int(parts[5])
        return ip,port
            
    def delete(self,remote_file):
        self.clientSocket.send(f'DELE {remote_file}\r\n'.encode())
        resp = self.receive_all(self.clientSocket)
        
    def pwd(self):
        self.clientSocket.send(f'XPWD\r\n'.encode())
        resp = self.receive_all(self.clientSocket)
        
    def ascii(self):
        self.clientSocket.send(f'TYPE A\r\n'.encode())
        resp = self.receive_all(self.clientSocket)
        self.type = "Ascii"
        
    def binary(self):
        self.clientSocket.send(f'TYPE I\r\n'.encode())
        resp = self.receive_all(self.clientSocket)
        self.type = "Binary"
        
    def cd(self,dir=''):
        if dir == '':
            dir = input('Remote directory ')
            if dir == '':
                print('cd remote directory.')
                return
        self.clientSocket.send(f'CWD {dir}\r\n'.encode())
        resp = self.receive_all(self.clientSocket)
        
    def get_data_socket(self):
        data_ip = self.clientSocket.getsockname()[0]
        
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.bind((data_ip,0))
        
        data_port = data_socket.getsockname()[1]
        temp = f"{data_ip}.{data_port//256}.{data_port%256}"
        ip_send = temp.replace('.',',')
        self.clientSocket.send(f'PORT {ip_send}\r\n'.encode())
        resp = self.receive_all(self.clientSocket)
        return data_socket
    
    def set_default(self):
        self.isConnect = False
        self.connectedServer = None
        self.username = None
        self.password = None
        self.type = "Binary"    