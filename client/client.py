import socket
import sys
import os
import pwinput
import hashlib
from cryptography.fernet import Fernet
from pprint import pprint
from user import User

HOST = "127.0.0.1"
PORT = 8000


class Client:

    __host = ""
    __port = -1
    __s = None
    __key = ''
    __current_dir = '/home'
    __user = None
    __look_up_table = {}

    def __init__(self, host = HOST, port = PORT):
        print("Setting up client")
        self.__host = host
        self.__port = port
        self.__current_dir = '/home'
        try:
            self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__s.connect((self.__host, self.__port))
            self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print ("Socket successfully created")
        except socket.error as err:
            print ("socket creation failed with error %s" %(err))

    def __login(self, username, password):

        tmp_string = "0 {} {}".format(username, password)

        # send login request to server
        self.__s.send(tmp_string.encode())

        # wait for response
        res_ = self.__s.recv(2048).decode()
        print(res_)

        return res_

    def __parseMsg(self, msg):
        # TODO I need to receive and return the group ID
        tmp_array = msg.split()
        if len(tmp_array) != 3:
            print("invalid response")
            return
        ack = 0
        try:
            ack = int(tmp_array[0])
        except ValueError:
            print("invalid response")
            return
        return ack, tmp_array[1], tmp_array[2]


    def __createFile(self, fileName):
        # for 'create' command
        print("Start Creating File...")
        try:
            tmp_string = "2 {}".format(fileName)
            self.__s.send(tmp_string.encode())

            res_ = self.__s.recv(2048).decode()
            print(res_)

        except Exception as err:
            print ("Error: %s %s" %(fileName, err))

        return

    def __parseCommand(self, command):
        tmp_array = command.split()
        return tmp_array

    def __displayFileContents(self, fileName):
        # for 'cat' command
        print("Start display File...")
        try:
            tmp_string = "3 {}".format(fileName)
            self.__s.send(tmp_string.encode())

            res_ = self.__s.recv(2048).decode()
            print(res_)

        except Exception as err:
            print ("Error: %s %s" %(fileName, err))

        return

    def __addFileContents(self, fileName, contents):
        # for 'echo' command
        print("Start adding contents to File...")
        try:
            tmp_string = "4 {} {}".format(fileName, contents)
            self.__s.send(tmp_string.encode())

            res_ = self.__s.recv(2048).decode()
            
            print(res_)

        except Exception as err:
            print ("Error: %s %s" %(fileName, err))

        return

    def __generateIntegrityCode(self, filename):
        
        integrity_filename = hashlib.md5(filename.encode()).hexdigest()
        with open(filename, 'rb') as ff:
            data = ff.read()    
            integrity_content = hashlib.md5(data).hexdigest()

        return integrity_filename, integrity_content
    
    def __verifyIntegrityCode(self, filename, integrity_filename, integrity_content):
        code1, code2 = self.__generateIntegrityCode(filename)

        if code1 == integrity_filename and code2 == integrity_content:
            return True

        else:
            return False


    def __createDirectory(self, directoryName):
        # for 'mkdir' command
        print("Start creating directory...")
        try:
            tmp_string = "5 {}".format(directoryName)
            self.__s.send(tmp_string.encode())

            res_ = self.__s.recv(2048).decode()
            
            # ack_, errorMsg_ = self.__parseMsg(res_)
            print(res_)

        except Exception as err:
            print ("Error: %s %s" %(directoryName, err))

        return

    def __changeDirectory(self, directoryName):
        # for 'cd' command
        print("Start creating directory...")
        try:
            tmp_string = "6 {}".format(directoryName)
            self.__s.send(tmp_string.encode())

            res_ = self.__s.recv(2048).decode()
            
            print(res_)

        except Exception as err:
            print ("Error: %s %s" %(directoryName, err))

        # print(self.__look_up_table)
        return

    # list all files and directories in current directory
    def __listDir(self):
        # for 'mkdir' command
        print("Start creating directory...")
        try:
            tmp_string = "7".format()
            self.__s.send(tmp_string.encode())

            res_ = self.__s.recv(2048).decode()
            
            # ack_, errorMsg_ = self.__parseMsg(res_)
            print(res_)

        except Exception as err:
            print ("Error: %s" %(err))

        # print(self.__look_up_table)
        return
    
    def __signUp(self, username, password):
        try:
            tmp_string = "1 {} {}".format(username, password)
            self.__s.send(tmp_string.encode())

            res_ = self.__s.recv(2048).decode()
            
            # ack_, errorMsg_ = self.__parseMsg(res_)
            print(res_)

        except Exception as err:
            print ("Error: %s" %(err))

        return
    
    def __rename(self, old_name, new_name):
        try:
            tmp_string = "8 {} {}".format(old_name, new_name)
            self.__s.send(tmp_string.encode())

            res_ = self.__s.recv(2048).decode()
            
            # ack_, errorMsg_ = self.__parseMsg(res_)
            print(res_)

        except Exception as err:
            print ("Error: %s" %(err))

        return

    def __givePermission(self, targetUsername, fileName):
        try:
            tmp_string = "9 {} {}".format(targetUsername, fileName)
            self.__s.send(tmp_string.encode())

            res_ = self.__s.recv(2048).decode()
            
            # ack_, errorMsg_ = self.__parseMsg(res_)
            print(res_)

        except Exception as err:
            print ("Error: %s" %(err))

        return
    
    
    def __exit(self):
        tmp_string = "11"
        self.__s.send(tmp_string.encode())

        res_ = self.__s.recv(2048).decode()
        
        # ack_, errorMsg_ = self.__parseMsg(res_)
        print(res_)

    def __delete(self, fileName):
        tmp_string = "10 {}".format(fileName)
        self.__s.send(tmp_string.encode())

        res_ = self.__s.recv(2048).decode()
        
        # ack_, errorMsg_ = self.__parseMsg(res_)
        print(res_)

    def __createGroup(self, groupName):
        tmp_string = "12 {}".format(groupName)
        self.__s.send(tmp_string.encode())

        res_ = self.__s.recv(2048).decode()
        
        # ack_, errorMsg_ = self.__parseMsg(res_)
        print(res_)

    def __addToGroup(self, userName, groupName):
        tmp_string = "13 {} {}".format(userName, groupName)
        self.__s.send(tmp_string.encode())

        res_ = self.__s.recv(2048).decode()
        
        # ack_, errorMsg_ = self.__parseMsg(res_)
        print(res_)
    # command dispatcher
    def __dispatchCommand(self, commandArray):
        if commandArray[0] == "create": 
            print("Receive Creating File Command")
            self.__createFile(commandArray[1])
        elif commandArray[0] == "cat":
            print("Receive Displaying File Command")
            self.__displayFileContents(commandArray[1])
        elif commandArray[0] == "echo":
            print("Receive Echo Command")
            self.__addFileContents(commandArray[1], ' '.join(commandArray[2:]))
        # case "verify":
        #     print("Receive Verify Command")
        #     self.__generateIntegrityCode(commandArray[1])
        elif commandArray[0] == "mkdir":
            print("Receive Mkdir Command")
            self.__createDirectory(commandArray[1])
        elif commandArray[0] == "cd":
            print("Receive Cd Command")
            self.__changeDirectory(commandArray[1])

        elif commandArray[0] == "ls":
            self.__listDir()
        elif commandArray[0] == "del":
            self.__delete(commandArray[1])
        elif commandArray[0] == "exit":
            self.__exit()
            print("Exit the SFS.")
            return 0
        elif commandArray[0] == "rename":
            self.__rename(commandArray[1], commandArray[2])

        elif commandArray[0] == "givep":
            self.__givePermission(commandArray[1], commandArray[2])

        # case "removep":
        #     self.__removePermission(commandArray[1], commandArray[2])

        # group creation should happen on server side
        # elif commandArray[0] == "createG":
        #     self.__createGroup(commandArray[1])
        # elif commandArray[0] == "add2G":
        #     self.__addToGroup(commandArray[1], commandArray[2])
        elif commandArray[0] == __:
            print("Not a valid command, please try again.")
        return 1






    # Start the client
    def start(self):

        U = User()
        self.__user = U
        while(1):
            flag = input("Do you want to 'signup' or 'login': ")
            if (flag == 'login'):
                break
            elif (flag == 'signup'):
                username_ = input("Please Enter Your Username: ")
                password_ = pwinput.pwinput(prompt='Please Enter Your Password: ')
                fail = self.__signUp(username_, password_)

                if not fail:
                    break

        while(1):
            username_ = input("Please Enter Your Username: ")
            password_ = pwinput.pwinput(prompt='Please Enter Your Password: ')

            login = self.__login(username_, password_)
            # if login succeed, break the while loop
            if(login[0] == '1'):
                break

        while(1):
            command_ = input("Please Enter Command (Enter 'help' to show a list of available commands): ")
            commandArray_ = self.__parseCommand(command_)
            endFlag = self.__dispatchCommand(commandArray_)

            if(not endFlag):
                break
