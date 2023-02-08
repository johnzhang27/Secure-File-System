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
    __current_dir = '/Home/'

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

        # send login request to server
        self.__s.send(tmp_string.encode())

        # wait for response
        res_ = self.__s.recv(2048).decode()
        print(res_)
        # parse message
        ack_, errorMsg_ = self.__parseMsg(res_)
        
        # if login succeed
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
            
        if not original:
            return
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
        
        if (not encrypted):
            return b''
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

    def __displayFileContents(self, fileName):
        # TODO this is for cat command
        decrypted_ = self.__DecryptFile(fileName)
        # f = open(fileName, "r")
        print(decrypted_.decode())

        return

    def __addFileContents(self, fileName, contents):
        # print(contents)
        fernet = Fernet(self.__key)

        decrypted_ = self.__DecryptFile(fileName)
        # f = open(fileName, "r")
        original_contents = decrypted_.decode()

        # contents = original_contents + '\n' + contents
        contents = original_contents + contents + '\n'
            
        # encrypting the file
        # https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3
        encrypted = fernet.encrypt(contents.encode())
        
        # opening the file in write mode and
        # writing the encrypted data
        with open(fileName, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
        return

    def __generateIntegrityCode(self, filename):
        
        integrity_filename = hashlib.md5(filename.encode()).hexdigest()
        with open(filename, 'rb') as ff:
            data = ff.read()    
            integrity_content = hashlib.md5(data).hexdigest()

        print(integrity_filename)
        print(integrity_content)
        return integrity_filename, integrity_content
    
    def __verifyIntegrityCode(self, filename, integrity_filename, integrity_content):
        code1, code2 = self.__generateIntegrityCode(filename)

        if code1 == integrity_filename and code2 == integrity_content:
            return True

        else:
            return False


    def __createDirectory(self, directoryName):
        try: 
            os.mkdir(directoryName)
        except OSError as error: 
            print(error)

    def __changeDirectory(self, directoryName):

        if (directoryName == '../'):
            try:
                os.chdir("..")
            except OSError as error: 
                print(error)
        else:
            try: 
                os.chdir(directoryName)
            except OSError as error: 
                print(error)

    def __listDir(self):
        print(*os.listdir(), sep='\n')

    def __showCurrentDirectory(self):
        print(os.getcwd())

    def __dispatchCommand(self, commandArray):
        match commandArray[0]:
            case "create": 
                print("Receive Creating File Command")
                self.__createFile(commandArray[1])
            case "cat":
                print("Receive Displaying File Command")
                self.__displayFileContents(commandArray[1])
            case "echo":
                print("Receive Echo Command")
                self.__addFileContents(commandArray[1], ' '.join(commandArray[2:]))
            case "verify":
                print("Receive Verify Command")
                self.__generateIntegrityCode(commandArray[1])
            case "mkdir":
                print("Receive Mkdir Command")
                self.__createDirectory(commandArray[1])
            case "cd":
                print("Receive Cd Command")
                self.__changeDirectory(commandArray[1])

            case "pwd":
                print("Receive Pwd Command")
                self.__showCurrentDirectory()

            case "ls":
                self.__listDir()

            case "exit":
                print("Exit the SFS.")
                return 0

            case __:
                print("Not a valid command, please try again.")
        return 1

    
    # def __displayFileContents(self, fileName):
    #     # TODO this is for cat command
    #     decrypted_ = self.__DecryptFile(fileName)
    #     # f = open(fileName, "r")
    #     print(decrypted_.decode())

    #     return

    # def __addFileContents(self, fileName, contents):
    #     # print(contents)
    #     fernet = Fernet(self.__key)

    #     decrypted_ = self.__DecryptFile(fileName)
    #     # f = open(fileName, "r")
    #     original_contents = decrypted_.decode()

    #     # contents = original_contents + '\n' + contents
    #     contents = original_contents + contents + '\n'
            
    #     # encrypting the file
    #     # https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3
    #     encrypted = fernet.encrypt(contents.encode())
        
    #     # opening the file in write mode and
    #     # writing the encrypted data
    #     with open(fileName, 'wb') as encrypted_file:
    #         encrypted_file.write(encrypted)
    #     return

    # def __generateIntegrityCode(self, filename):
        
    #     integrity_filename = hashlib.md5(filename.encode()).hexdigest()
    #     with open(filename, 'rb') as ff:
    #         data = ff.read()    
    #         integrity_content = hashlib.md5(data).hexdigest()

    #     print(integrity_filename)
    #     print(integrity_content)
    #     return integrity_filename, integrity_content
    
    # def __verifyIntegrityCode(self, filename, integrity_filename, integrity_content):
    #     code1, code2 = self.__generateIntegrityCode(filename)

    #     if code1 == integrity_filename and code2 == integrity_content:
    #         return True

    #     else:
    #         return False


    # def __createDirectory(self, directoryName):
    #     try: 
    #         os.mkdir(directoryName)
    #     except OSError as error: 
    #         print(error)  



    def start(self):

        while(1):
            username_ = input("Please Enter Your Username: ")
            password_ = pwinput.pwinput(prompt='Please Enter Your Password: ')

            login_flag = self.__login(username_, password_)
            # if login succeed, break the while loop
            if(login_flag):
                break
        
        group_ = 1
        # TODO after login, we should initialize an user instance here.
        U = User(username_, password_, group_)


        while(1):
            command_ = input("Please Enter Command (Enter 'help' to show a list of available commands): ")
            commandArray_ = self.__parseCommand(command_)
            endFlag = self.__dispatchCommand(commandArray_)

            if(not endFlag):
                break

            # self.__addFileContents(commandArray_[1], "This is test")

            # self.__displayFileContents(commandArray_[1])
            # self.__encryptFile('test_txt.txt')
            # break
