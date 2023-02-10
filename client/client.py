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
    __user = None
    __look_up_table = {}

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
        # print(res_)
        # parse message
        ack_, errorMsg_, group_id = self.__parseMsg(res_)
        
        # if login succeed
        if int(ack_):
            print("User Login succeed.")
            return 1, group_id
        else:
            print("User Login failed: {}".format(errorMsg_))
            return 0, -1

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
            tmp_key_ = Fernet.generate_key()
            # 9 for new key (new file)
            # 9 #FILENAME #ENCRYPTIONKEY #FULLPATH
            # current_dir = os.getcwd()
            # # full_path = os.path.join(current_dir, fileName)
            # tmp_string = "9 {} {} {}".format(fileName, tmp_key_, current_dir)
            # self.__s.send(tmp_string.encode())

            f = open(fileName, "x")
            encrypted_fileName = self.__encryptFileName(fileName, tmp_key_)
            self.__encryptFile(encrypted_fileName, tmp_key_)


            current_dir = os.getcwd()
            # full_path = os.path.join(current_dir, fileName)
            tmp_string = "9 {} {} {}".format(encrypted_fileName.decode(), tmp_key_.decode(), current_dir)
            self.__s.send(tmp_string.encode())

            # current_dir = os.getcwd()
            # # full_path = os.path.join(current_dir, new_fileName)
            # tmp_string = "9 {} {} {}".format(new_fileName, tmp_key_, current_dir)
            # self.__s.send(tmp_string.encode())

            self.__look_up_table[(fileName, current_dir)] = encrypted_fileName.decode()

        except Exception as err:
            print ("Error: %s %s" %(fileName, err))

        # print(self.__look_up_table)
        return

    def __encryptFile(self, fileName, key):
        print("Start File Encryption...")

        # tmp_key_ = self.__requestKey(fileName)
        # if not tmp_key_:
        #     tmp_key_ = Fernet.generate_key()
        #     # 9 for new key (file contents)
        #     # 9 #FILENAME #ENCRYPTIONKEY
        #     tmp_string = "9 {} {}".format(fileName, tmp_key_)
        #     self.__s.send(tmp_string.encode())

        fernet = Fernet(key)
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

    # this should only be called when creating new file
    def __encryptFileName(self, fileName, key):
        print("Start File Name Encryption...")
        # key = Fernet.generate_key()
        # self.__key = key
        #TODO send encyption key to server

        # tmp_key_ = self.__requestKey(fileName)
        # if not tmp_key_:
        #     tmp_key_ = Fernet.generate_key()
        #     # 10 #FILENAME #ENCRYPTIONKEY
        #     tmp_string = "10 {} {}".format(fileName, tmp_key_)

        #     # send login request to server
        #     self.__s.send(tmp_string.encode())

        fernet = Fernet(key)
        # encrypting the file name
        encrypted = fernet.encrypt(fileName.encode())
        
        # opening the file in write mode and
        # writing the encrypted data
        os.rename(fileName, encrypted)
        return encrypted

    def __requestKey(self, fileName, fullPath):
        #TODO send request to server ask for a list of files
        # 8 #FILENAME #FULLPATH
        # current_dir = os.getcwd()
        # full_path = os.path.join(current_dir, fileName)
        tmp_string = "8 {} {}".format(fileName, fullPath)

        # send login request to server
        self.__s.send(tmp_string.encode())

        # wait for response
        print("request key")
        key_ = self.__s.recv(2048).decode()
        # print(key_)

        return key_  

    def __DecryptFile(self, encrypted_fileName, fullPath):

        # fileName = self.__look_up_table[(encrypted_fileName,fullPath)]

        tmp_key_ = self.__requestKey(encrypted_fileName, fullPath)

        if not tmp_key_ or tmp_key_ == '0':
            print("The file doesn't exist in databse, please make sure you create the file using this SFS")
        # using the key
        fernet = Fernet(tmp_key_)
        decrypted = b''
        try:
            
            # opening the encrypted file
            with open(os.path.join(fullPath, encrypted_fileName), 'rb') as enc_file:
                encrypted = enc_file.read()
            
            if (not encrypted):
                return b''
            # decrypting the file
            decrypted = fernet.decrypt(encrypted)
        except Exception as err:
            print ("Error: Your file has been modified or removed %s" %(err))

        
        # # opening the file in write mode and
        # # writing the decrypted data
        # with open(fileName, 'wb') as dec_file:
        #     dec_file.write(decrypted)
        return decrypted

    def __DecryptFileName(self, encrypted_fileName, fullPath):

        # fileName = self.__look_up_table[(encrypted_fileName,fullPath)]
        tmp_key_ = self.__requestKey(encrypted_fileName, fullPath)

        if not tmp_key_ or tmp_key_ == '0':
            print("The file doesn't exist in databse, please make sure you create the file using this SFS")
        # using the key
        fernet = Fernet(tmp_key_)
        decrypted = b''
        try:
            decrypted = fernet.decrypt(encrypted_fileName)
        except Exception as err:
            print ("Error: Your fileName has been modified or removed %s" %(err))

        return decrypted

    def __parseCommand(self, command):
        tmp_array = command.split()
        return tmp_array

    def __displayFileContents(self, fileName):
        current_dir = os.getcwd()
        # full_path = os.path.join(current_dir, fileName)
        # print(fileName)
        # print(full_path)
        encrypted_fileName = self.__look_up_table[(fileName, current_dir)]
        # print(tmp_fileName)
        # TODO this is for cat command
        decrypted_ = self.__DecryptFile(encrypted_fileName, current_dir)
        # f = open(fileName, "r")
        print(decrypted_.decode())

        return

    def __addFileContents(self, fileName, contents):
        current_dir = os.getcwd()
        # full_path = os.path.join(current_dir, fileName)
        encrypted_fileName = self.__look_up_table[(fileName, current_dir)]
        # print(contents)
        tmp_key_ = self.__requestKey(encrypted_fileName, current_dir)
        if not tmp_key_:
            print("The file doesn't exist in databse, please make sure you create the file using this SFS")
            return
        fernet = Fernet(tmp_key_)

        decrypted_ = self.__DecryptFile(encrypted_fileName, current_dir)
        # f = open(fileName, "r")
        original_contents = decrypted_.decode()

        # contents = original_contents + '\n' + contents
        contents = original_contents + contents + '\n'
            
        # encrypting the file
        # https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3
        encrypted = fernet.encrypt(contents.encode())
        
        # opening the file in write mode and
        # writing the encrypted data
        with open(encrypted_fileName, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
        return

    def __generateIntegrityCode(self, filename):
        
        integrity_filename = hashlib.md5(filename.encode()).hexdigest()
        with open(filename, 'rb') as ff:
            data = ff.read()    
            integrity_content = hashlib.md5(data).hexdigest()

        # print(integrity_filename)
        # print(integrity_content)
        return integrity_filename, integrity_content
    
    def __verifyIntegrityCode(self, filename, integrity_filename, integrity_content):
        code1, code2 = self.__generateIntegrityCode(filename)

        if code1 == integrity_filename and code2 == integrity_content:
            return True

        else:
            return False


    def __createDirectory(self, directoryName):
        #TODO might change the structure later.
        try: 
            os.mkdir(directoryName)
        except OSError as error: 
            print(error)
        current_dir = os.getcwd()
        full_path = os.path.join(current_dir, directoryName)
        tmp_string = "5 {} {} {}".format(self.__user.getUsername(), self.__user.getGroup(), full_path)

        # send login request to server
        # 5 #USERNAME #GROUPID #DIRECTORYPATH
        self.__s.send(tmp_string.encode())

    def __changeDirectory(self, directoryName):

        if (directoryName == '../'):
            try:
                os.chdir("..")
            except OSError as error: 
                print(error)
        else:
            try: 
                current_dir = os.getcwd()
                full_path = os.path.join(current_dir, directoryName)
                tmp_string = "4 {} {} {}".format(self.__user.getUsername(), self.__user.getGroup(), full_path)

                # send login request to server
                # 4 #USERNAME #GROUPID #DIRECTORYPATH
                # RES: 1 or 0
                self.__s.send(tmp_string.encode())
                ans_ = self.__s.recv(2048).decode()
                print("change directory %s", ans_)
                if ans_ == '1':
                    os.chdir(full_path)
                else:
                    print("You don't belong to the group")
            except OSError as error: 
                print(error)

    # list all files and directories in current directory
    def __listDir(self):
        # get the list using os command
        tmp_list = os.listdir()
        current_dir = os.getcwd()
        # since all files are encrypted so we have decrypted them
        for ele in tmp_list:
            # full_path = os.path.join(current_dir, ele)
            # print(full_path)
            # print(ele)
            if not os.path.isdir(ele) and ele in self.__look_up_table.values():

                tmp_fileName = self.__DecryptFileName(ele, current_dir)
                print(tmp_fileName.decode())
            else:
                print(ele)
        # print(*os.listdir(), sep='\n')

    # display current directory
    def __showCurrentDirectory(self):
        print(os.getcwd())


    # get a list of files that belongs to the current user or the user has permission to access it
    def __getFileList(self, username):
        #TODO send request to server ask for a list of files
        tmp_string = "7 {}".format(username)

        # send login request to server
        # 7 #USERNAME
        self.__s.send(tmp_string.encode())

        # wait for response
        file_list_ = self.__s.recv(2048).decode()
        # key_list_ = self.__s.recv(2048).decode()
        # print(file_list_)

        return file_list_

    # get a list of files that belongs to the current user or the user has permission to access it
    def __getFullPathList(self, username):
        #TODO send request to server ask for a list of files
        tmp_string = "6 {}".format(username)

        # send login request to server
        # 7 #USERNAME
        self.__s.send(tmp_string.encode())

        # wait for response
        full_path_list_ = self.__s.recv(2048).decode()
        # key_list_ = self.__s.recv(2048).decode()
        # print(full_path_list_)

        return full_path_list_

    # command dispatcher
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
            # case "verify":
            #     print("Receive Verify Command")
            #     self.__generateIntegrityCode(commandArray[1])
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






    # Start the client
    def start(self):

        U = User()
        self.__user = U
        while(1):
            username_ = input("Please Enter Your Username: ")
            password_ = pwinput.pwinput(prompt='Please Enter Your Password: ')

            login_flag, group_id_ = self.__login(username_, password_)
            # if login succeed, break the while loop
            if(login_flag):
                U.setUsername(username_)
                U.setPassword(password_)
                U.setGroup(group_id_)
                print("group ID is: " + U.getGroup())
                break
        
        # group_ = 1
        # # TODO after login, we should initialize an user instance here.
        # U = User(username_, password_, group_)

        # TODO after the user login, we need to check to see if any file is modified outside the SFS
        file_list_ = self.__getFileList(U.getUsername())
        full_path_list_ = self.__getFullPathList(U.getUsername())

        if file_list_ != '0':
            tmp_file_list_ = self.__parseCommand(file_list_)
            tmp_full_path_list_ = self.__parseCommand(full_path_list_)

            # They have to be in same order
            U.setFilelist(tmp_file_list_)
            U.setPathlist(tmp_full_path_list_)

            # print(self.__user.getFilelist()) 

            #TODO iterate over the file list and decrypt every single file, if the file is modified, raise an error message

            for (file, path) in zip(self.__user.getFilelist(), self.__user.getPathlist()):
                # if we can't decrypt the file then it means someone has modified the content.
                # print("I'm here")

                self.__DecryptFile(file, path)
                # print("I'm here2")
                tmp_real_name = self.__DecryptFileName(file, path)
                
                self.__look_up_table[(tmp_real_name.decode(), path)] = file
            print(self.__look_up_table)

        while(1):
            command_ = input("Please Enter Command (Enter 'help' to show a list of available commands): ")
            commandArray_ = self.__parseCommand(command_)
            endFlag = self.__dispatchCommand(commandArray_)

            if(not endFlag):
                break
