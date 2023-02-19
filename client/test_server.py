import socket 
import threading
from cryptography.fernet import Fernet
from user import User


HEADER = 1024
HOST = "127.0.0.1"
PORT = 8000
# SERVER = socket.gethostbyname(socket.gethostname())
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

__key = Fernet.generate_key()
key2 = Fernet.generate_key()
user_list = [User("John", 123, 1), User("Jason", 123, 1)]

def parseCommand(command):
    tmp_array = command.split()
    return tmp_array

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    # __key = Fernet.generate_key()
    connected = True
    UU = User()
    while connected:
        msg = conn.recv(HEADER).decode()
        if msg:
            # msg_length = int(msg_length)
            # msg = conn.recv(msg_length).decode()
            # if msg == DISCONNECT_MESSAGE:
            #     connected = False
            print(f"[{addr}] {msg}")
            print(msg[0])
            tmp = parseCommand(msg)
            if tmp[0] == '0':
                print(tmp)
                if tmp[1] == 'John':
                    UU = user_list[0]
                else:
                    UU = user_list[1]

                # user_list.append(User())
                print("current user is: ")
                print(UU.getUsername())
                conn.send("{} success {}".format(1, 1).encode())
            elif tmp[0] == '7':
                print(tmp)
                if UU.getFilelist():
                    file_list = ' '.join(UU.getFilelist())
                    # key_list = __key.decode() + " " + __key.decode() + " " + __key.decode()
                    conn.send(file_list.encode())
                    # conn.send(key_list.encode())
                    print("done")
                else:
                    conn.send(b'0')

            elif tmp[0] == '6':
                print(tmp)
                if UU.getPathlist():
                    file_list = ' '.join(UU.getPathlist())
                    # key_list = __key.decode() + " " + __key.decode() + " " + __key.decode()
                    conn.send(file_list.encode())
                    # conn.send(key_list.encode())
                    print("done")
                else:
                    conn.send(b'0')

            elif tmp[0] == '8':
                print(tmp)
                flag = False
                print(UU.getFilelist())
                print(UU.getPathlist())
                for file, key, path in zip(UU.getFilelist(), UU.getKeylist(), UU.getPathlist()):
                    if file == tmp[1] and path == tmp[2]:
                        print("key is: ")
                        print(key)
                        conn.send(key.encode())
                        flag = True
                        break
                if not flag:     
                    conn.send(b'0')
            
            elif tmp[0] == '4':
                conn.send("1".encode())

            # elif tmp[0] == '5':
            #     conn.send("1".encode())

            elif tmp[0] == '9':
                print(tmp)
                tmp_list = UU.getFilelist()
                tmp_list.append(tmp[1])
                UU.setFilelist(tmp_list)

                tmp_list2 = UU.getKeylist()
                tmp_list2.append(tmp[2])
                UU.setKeylist(tmp_list2)

                tmp_list3= UU.getPathlist()
                tmp_list3.append(tmp[3])
                UU.setPathlist(tmp_list3)
            
    conn.close()
        

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[STARTING] server is starting...")
start()