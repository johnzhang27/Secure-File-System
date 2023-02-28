import socket
import sys
import os
import pwinput
import hashlib
import shutil
from cryptography.fernet import Fernet

class FileManager:

    relative_path = None
    current_path = None
    home_path = None
    # fileName = '1.txt'

    def __init__(self):
        self.relative_path = '\\home'
        if (os.path.exists('home_dir')):
            os.chdir('home_dir')
        else:
            os.mkdir('home_dir')
            os.chdir('home_dir')
        self.current_path = os.getcwd()
        self.home_path = os.getcwd()
        # print("in constructor: ")
        # print(os.getcwd())
        print(self.relative_path)
    
    def createFile(self, fileName):
        """
        Function for creating a file in the current directory
        Args: fileName, the plain file name received from user.
        Returns: a list which is [encryoted_file_name, plain_absolute_path, encryoted_absolute_path, key]
        """
        print("Start Creating File...")
        tmp_list = []
        try:
            tmp_key_ = Fernet.generate_key()


            f = open(fileName, "x")
            f.close()
            # encryt file name
            encrypted_fileName = self.encryptFileName(fileName, tmp_key_)
            # encryot absolute path
            absolute_path = os.path.join(self.current_path, encrypted_fileName)
            encrypted_absolute_path = self.encryptFileName(absolute_path, tmp_key_)

            self.renameFile(fileName, encrypted_fileName)

            # encrypt file contents (should be empty now)
            self.encryptFile(encrypted_fileName, tmp_key_)

            tmp_list.append(encrypted_fileName)
            tmp_list.append(absolute_path)
            tmp_list.append(encrypted_absolute_path)
            tmp_list.append(tmp_key_)

        except Exception as err:
            print ("Error: %s %s" %(fileName, err))

        return tmp_list
    

    def encryptFile(self, encrypted_fileName, key):

        """
        Function for encrypt file contents
        Args: encrypted_fileName
              key, encrypotion key
        Returns: None
        """
        print("Start File Encryption...")

        fernet = Fernet(key)
        with open(encrypted_fileName, 'rb') as file:
            original = file.read()
            
        if not original:
            return
        encrypted = fernet.encrypt(original)

        with open(encrypted_fileName, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
        return


    def encryptFileName(self, fileName, key):
        """
        Function for encrypt file name
        Args: fileName, plain file name received from user
              key, encrypotion key
        Returns: encrypted file name
        """
        print("Start File Name Encryption...")
        fernet = Fernet(key)
        encrypted = fernet.encrypt(fileName.encode())
    
        return encrypted.decode()

    # rename the file, fileName to encrypted file name
    def renameFile(self, fileName, encrypted):
        os.rename(fileName, encrypted)
        return 
    

    def renameFile_public(self, fileName, complete_file_dic, new_fileName):
        """
        Function for adding new contents to a file
        Args: fileName, plain file name received from user
              complete_file_dic, {key: encrypted file absolute path, value: pair(encryption key, encrypted file name)}
              new_fileName, plain new_fileName received from user
        Returns: a list [encrypted new file name, plain absolute path, encrypted absolute path, encrypted old file name]
        """
        # get a file lsit in the current directory
        file_list = self.getFileListInCurrentDir(complete_file_dic)
        tmp_len = len(fileName)
        return_list = []
        # iterate over the list
        for f in file_list.keys():
            # decrypt every element
            tmp = self.DecryptFileName(file_list[f][1],file_list[f][0])
            # if the decrypted filename match what user passed
            if tmp == fileName:
 
                encrypted_new_name = self.encryptFileName(new_fileName, file_list[f][0])
                # encryot absolute path
                absolute_path = os.path.join(self.current_path, encrypted_new_name)
                encrypted_absolute_path = self.encryptFileName(absolute_path, file_list[f][0])

                os.rename(file_list[f][1], encrypted_new_name)
                print("old name: ")
                print(file_list[f][1])
                print("new name")
                print(encrypted_new_name)

                return_list.append(encrypted_new_name)
                return_list.append(absolute_path)
                return_list.append(encrypted_absolute_path)
                return_list.append(f)
                # update the complete_file_dic
                complete_file_dic[encrypted_absolute_path] = (file_list[f][0], encrypted_new_name)
                complete_file_dic.pop(f)
                break

        #!!!!!!!!!!!!!!!! IMPORTANT !!!!!!!!!!!!!!!!!
        # You need to update the record with old encrypted file name in database
        return return_list
    

    def DecryptFile(self, encrypted_fileName, key):
        """
        Function for decrypt file contents (only for files in the current directory)
        Args: encryoted_fileName
              key, encrypotion key
        Returns: decrypted contents
        """
        tmp_key_ = key

        if not tmp_key_ or tmp_key_ == '0':
            print("The file doesn't exist in databse, please make sure you create the file using this SFS")
        # using the key
        fernet = Fernet(tmp_key_)
        decrypted = b''
        try:
            
            # opening the encrypted file
            with open(encrypted_fileName, 'rb') as enc_file:
                encrypted = enc_file.read()
            
            if (not encrypted):
                return decrypted.decode()
            # decrypting the file
            decrypted = fernet.decrypt(encrypted)
        except Exception as err:
            print ("Error: Your file has been modified or removed %s" %(err))

        return decrypted.decode()


    def DecryptFileName(self, encrypted_fileName, key):

        tmp_key_ = key

        if not tmp_key_ or tmp_key_ == '0':
            print("The file doesn't exist in databse, please make sure you create the file using this SFS")
        # using the key
        fernet = Fernet(tmp_key_)
        decrypted = b''
        try:
            decrypted = fernet.decrypt(encrypted_fileName)
        except Exception as err:
            print ("Error: Your fileName has been modified or removed %s" %(err))

        return decrypted.decode()
    
    # private function, you don't need to worry about this
    def getFileListInCurrentDir(self, complete_file_dic):
        current_files_and_directories = os.listdir()

        file_list = {}
        for ele in complete_file_dic:
            if complete_file_dic[ele][1] in current_files_and_directories:
                file_list[ele] = (complete_file_dic[ele][0], complete_file_dic[ele][1])

        # print("files in current directory: ")  
        # print(file_list)

        return file_list
    

    def displayFileContents(self, fileName, complete_file_dic):
        """
        Function for display file contents
        Args: fileName, plain file name received from user
              complete_file_dic, {key: encrypted file absolute path, value: pair(encryption key, encrypted filename)}
        Returns: decrypted contents
        """

        # print('11')
        file_list = self.getFileListInCurrentDir(complete_file_dic)
        # print('22')
        contents = ''
        for f in file_list.keys():
            tmp = self.DecryptFileName(file_list[f][1],file_list[f][0])
            if tmp == fileName:
                contents = self.DecryptFile(file_list[f][1],file_list[f][0])
        # print('33')
        # print(contents)
        return contents


    def addFileContentsWrapper(self, fileName, complete_file_dic, contents):
        """
        Function for adding new contents to a file
        Args: fileName, plain file name received from user
              complete_file_dic, {key: encrypted file absolute path, value: pair(encryption key, encrypted filename)}
              contents, plain contents received from user
        Returns: None
        """
        file_list = self.getFileListInCurrentDir(complete_file_dic)
        tmp_len = len(fileName)
        for f in file_list:
            tmp = self.DecryptFileName(file_list[f][1],file_list[f][0])
            if tmp == fileName:
                self.addFileContents(file_list[f][1], contents, file_list[f][0])
        return
    
    def addFileContents(self, encrypted_fileName, contents, key):

        fernet = Fernet(key)

        decrypted_ = self.DecryptFile(encrypted_fileName, key)
        original_contents = decrypted_

        contents = original_contents + contents + '\n'
            
        # encrypting the file
        # https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3
        encrypted = fernet.encrypt(contents.encode())
        
        # opening the file in write mode and
        # writing the encrypted data
        with open(encrypted_fileName, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
        return


    def createDirectory(self, directoryName):
        """
        Function for creating new file directory
        Args: directoryName, received from user
        Returns: [encrypted directory name, plain absolute path, encrypted absolute path, key]
        """
        #TODO might change the structure later.
        try: 
            os.mkdir(directoryName)
        except OSError as error: 
            print(error)

        tmp_key_ = Fernet.generate_key()

        encrypted_dir = self.encryptDirectory(directoryName, tmp_key_)

        full_path = os.path.join(self.current_path, encrypted_dir)

        encrypted_path = self.encryptDirectory(full_path, tmp_key_)
        print(self.current_path)
        os.rename(directoryName, encrypted_dir)

        # tmp_string = "{} {} {}".format(full_path, encrypted_dir, tmp_key_)

        # TODO you will need encrypted absolue path and encrypoted directory name
        tmp_list = []
        tmp_list.append(encrypted_dir)
        tmp_list.append(full_path)
        tmp_list.append(encrypted_path)
        tmp_list.append(tmp_key_)

        return tmp_list
    

    def encryptDirectory(self, directory, key):
        print("Start File Name Encryption...")
        fernet = Fernet(key)
        encrypted = fernet.encrypt(directory.encode())
    
        return encrypted.decode()

    def decryptDirectory(self, encrypted_directory, key):
        tmp_key_ = key

        if not tmp_key_ or tmp_key_ == '0':
            print("The file doesn't exist in databse, please make sure you create the file using this SFS")
        # using the key
        fernet = Fernet(tmp_key_)
        decrypted = b''
        try:
            decrypted = fernet.decrypt(encrypted_directory)
        except Exception as err:
            print ("Error: Your fileName has been modified or removed %s" %(err))

        return decrypted.decode()
    

    def changeDirectory(self, path, lookup_table_v2):
        """
        Function for changing directory
        Args: path, plain path received from user
              lookup_table_v2: {key: plain directory name received from user, value: encrypted directory name not path}
        Returns: None
        """
        if (path == '../'):
            try:
                if self.relative_path == '\\home':
                    return
                else:
                    os.chdir("..")
                    s_list = self.relative_path.split("\\")

                    # Remove the last element of the list
                    s_list = s_list[:-1]

                    # Join the list back into a string using the '/' character
                    new_s = "\\".join(s_list)

                    self.relative_path = new_s
                    self.current_path = os.getcwd()

            except OSError as error: 
                print(error)
        else:
            try: 
                print("change directory")
                os.chdir(lookup_table_v2[path])
                self.current_path = os.getcwd()
                self.relative_path = self.relative_path + '\\' + path
            except OSError as error: 
                print(error)


    def listDir(self, complete_file_dic):

        """
        Function for listing all files and directories in the current directory
        Args: lookupTable, {key: encrypted file absolute path, value: encryption key}
        Returns: None
        """
        # get the list using os command
        tmp_list = os.listdir()
        # current_dir = os.getcwd()
        buffer = []
        # since all files are encrypted so we have decrypted them
        current_dir_list = self.getFileListInCurrentDir(complete_file_dic)
        for ele in current_dir_list:
            if current_dir_list[ele][1] in tmp_list:
                if not os.path.isdir(current_dir_list[ele][1]):
                    tmp_fileName = self.DecryptFileName(current_dir_list[ele][1], current_dir_list[ele][0])
                    buffer.append(tmp_fileName)
                else:
                    tmp_dirName = self.decryptDirectory(current_dir_list[ele][1], current_dir_list[ele][0])
                    buffer.append(tmp_dirName)
            else:
                buffer.append(ele)

        return buffer
    

    def generateLookupTable(self, complete_file_dic):
        # get a file lsit in the current directory
        file_list = self.getFileListInCurrentDir(complete_file_dic)
        lt2 = {}
        # iterate over the list
        for f in file_list:
            if os.path.isdir(file_list[f][1]):
                tmp = self.DecryptFileName(file_list[f][1],file_list[f][0])
                lt2[tmp] = file_list[f][1]

        return lt2
    # 0 for directory and 1 for file

    def generateIntegrityCode(self, abs_path, encrypted_filename):
        
        integrity_filename = hashlib.md5(encrypted_filename.encode()).hexdigest()
        with open(abs_path, 'rb') as ff:
            data = ff.read()    
            integrity_content = hashlib.md5(data).hexdigest()

        return integrity_filename, integrity_content

    def generateIntergityCodeForDirectory(self, enc_dir_name):
        return hashlib.md5(enc_dir_name.encode()).hexdigest()
    
    def verifyIntegrityCode(self, abs_path, enc_file_name, integrity_filename, integrity_content):
        if not os.path.exists(abs_path):
            return False

        code1, code2 = self.generateIntegrityCode(abs_path, enc_file_name)

        if code1 == integrity_filename and code2 == integrity_content:
            return True

        else:
            return False
    
    def verifyIntergityCodeForDirectory(self, abs_path):
        return os.path.exists(abs_path)

    def resetToHomePath(self):
        self.current_path = self.home_path
        self.relative_path = "\\home"
        os.chdir(self.current_path)

    # https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
    def deleteFile(self, filename, lookup_table):
        file_list = self.getFileListInCurrentDir(lookup_table)
        for file in file_list:
            dec_file = self.DecryptFileName(file_list[file][1], file_list[file][0])
            if dec_file == filename:
                if os.path.isfile(file_list[file][1]):
                    os.remove(file_list[file][1])
                else:
                    shutil.rmtree(file_list[file][1])
                return
        return