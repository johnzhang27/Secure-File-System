import socket
import sys
import os
import pwinput
from cryptography.fernet import Fernet

HOST = "127.0.0.1"
PORT = 8000


class Client:

    __host = ""
    __port = -1
    __s = None
    __key = ''

    def __init__(self, host = HOST, port = PORT):
        print("Setting up client")
        self.__key = Fernet.generate_key()
        self.__host = host
        self.__port = port
        try:
            self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__s.connect((self.__host, self.__port))
            self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print ("Socket successfully created")
        except socket.error as err:
            print ("socket creation failed with error %s" %(err))

    def __login(self, username, password):

        tmp_string = "0 {} {}".format(username, password)
        self.__s.send(tmp_string.encode())
        res_ = self.__s.recv(2048).decode()
        print(res_)
        ack_, errorMsg_ = self.__parseMsg(res_)

        if int(ack_):
            print("User creation succeed.")
            return 1
        else:
            print("User creation failed: {}".format(errorMsg_))
            return 0

    def __parseMsg(self, msg):

        tmp_array = msg.split()
        if len(tmp_array) != 2:
            print("invalid response")
            return
        ack = 0
        try:
            ack = int(tmp_array[0])
        except ValueError:
            print("invalid response")
            return
        return ack, tmp_array[1]


    def __createFile(self, fileName):
        # for 'create' command
        print("Start Creating File...")
        f = open(fileName, "x")
        self.__encryptFile(fileName)
        return

    def __encryptFile(self, fileName):
        print("Start File Encryption...")
        # key = Fernet.generate_key()
        # self.__key = key
        #TODO send encyption key to server


        fernet = Fernet(self.__key)
        # opening the original file to encrypt
        with open(fileName, 'rb') as file:
            original = file.read()
            
        # encrypting the file
        encrypted = fernet.encrypt(original)
        
        # opening the file in write mode and
        # writing the encrypted data
        with open(fileName, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
        return


    def __DecryptFile(self, fileName):

        # using the key
        fernet = Fernet(self.__key)
        
        # opening the encrypted file
        with open(fileName, 'rb') as enc_file:
            encrypted = enc_file.read()
        
        # decrypting the file
        decrypted = fernet.decrypt(encrypted)
        
        # # opening the file in write mode and
        # # writing the decrypted data
        # with open(fileName, 'wb') as dec_file:
        #     dec_file.write(decrypted)
        return decrypted

    def __parseCommand(self, command):
        tmp_array = command.split()
        return tmp_array


    def __dispatchCommand(self, commandArray):
        match commandArray[0]:
            case "create": 
                print("Receive Creating File Command")
                self.__createFile(commandArray[1])
        return

    def __displayFileContents(self, fileName):
        # TODO this is for cat command
        decrypted_ = self.__DecryptFile(fileName)
        # f = open(fileName, "r")
        print(decrypted_.decode())

        return

    def __addFileContents(self, fileName, contents):
        fernet = Fernet(self.__key)
            
        # encrypting the file
        encrypted = fernet.encrypt(contents.encode())
        
        # opening the file in write mode and
        # writing the encrypted data
        with open(fileName, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
        return


    def start(self):

        while(1):
            username_ = input("Please Enter Your Username: ")
            password_ = pwinput.pwinput(prompt='Please Enter Your Password: ')

            login_flag = self.__login(username_, password_)

            if(login_flag):
                break

        while(1):
            command_ = input("Please Enter Command (Enter 'help' to show a list of available commands): ")
            commandArray_ = self.__parseCommand(command_)
            self.__dispatchCommand(commandArray_)

            self.__addFileContents(commandArray_[1], "This is test")

            self.__displayFileContents(commandArray_[1])
            # self.__encryptFile('test_txt.txt')
            break
