import socket
import os
import database_manager
import file_manager
import traceback

# Server of the SFS

# Socket setup and config based on:
# https://github.com/aianta/cmput404-tcp-lab

HOST = "127.0.0.1"
PORT = 8000

class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.db = database_manager.DatabaseManager()
        self.file_manager = file_manager.FileManager()
        self.current_user = None

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        # self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.listen()
        while True: 
            conn, addr = self.socket.accept()
            self.handle_request(conn)

    def close_server(self):
        if self.socket != None:
            self.socket.close()
        self.db.close_session()

    def handle_request(self, conn):
        with conn:
            rec_data = b""
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # rec_data += data
                ans = self.parse_rec_data(data, conn)
    
    def parse_rec_data(self, rec_data, conn):
        rec_string = rec_data.decode()
        print(rec_string)
        recStringArray = rec_string.split()
        commandCode = 0
        try:
            commandCode = int(recStringArray[0])
        except ValueError:
            #send error response: improper command
            conn.sendall("Improper command".encode())
            return False
        if (commandCode == 0):
            if len(recStringArray) != 3:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.login(recStringArray[1], recStringArray[2]).encode())
        elif (commandCode == 1):
            if len(recStringArray) != 3:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.registerUser(recStringArray[1], recStringArray[2]).encode())
        elif (commandCode == 2):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.createFile(recStringArray[1]).encode())
        elif (commandCode == 3):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.displayContents(recStringArray[1]).encode())
        elif (commandCode == 4):
            if len(recStringArray) != 3:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.editFile(recStringArray[1], recStringArray[2]).encode())
        elif (commandCode == 5):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.createDirectory(recStringArray[1]).encode())
        elif (commandCode == 6):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.changeDirectory(recStringArray[1]).encode())
        elif (commandCode == 7):
            if len(recStringArray) != 1:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.displayDirectoryContent().encode())
        elif (commandCode == 8):
            if len(recStringArray) != 3:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.renameFile(recStringArray[1], recStringArray[2]).encode())
        elif (commandCode == 9):
            if len(recStringArray) != 3:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.changePermissionMode(recStringArray[1], recStringArray[2]).encode())
        elif (commandCode == 10):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.deleteFile(recStringArray[1]).encode())
        elif (commandCode == 11):
            conn.sendall(self.logout().encode())
            return True
        elif (commandCode == 12):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.createGroup(recStringArray[1]).encode())
        elif (commandCode == 13):
            if len(recStringArray) != 3:
                 #send error response: improper command
                conn.sendall("Improper command".encode())
                return False
            conn.sendall(self.addUserToGroup(recStringArray[1], recStringArray[2]).encode())
        else:
            conn.sendall("Improper command".encode())
            return False

    def login(self, username, password):
        if self.current_user != None:
            return "Already logged in!"
        user_obj = self.db.check_user_exists(username)
        if user_obj == None:
            return "User does not exist"
        if not self.db.login_in_user(username, password):
            return "Password does not match"
        self.current_user = user_obj
        returnStr = ""
        # Change directory to home directory of user
        returnStr += self.changeDirectory(self.current_user.user_id) + "\n"
        # Check intergity of files 
        compFiles = self.checkIntergityOfFiles()
        if (compFiles != []):
            returnStr += "The following files have been changed by an unauthorized user since your last login: \n"
            for file in self.getPlainTextFilePaths(compFiles):
                returnStr += file + "\n"
        return '1\n'+returnStr + "Successfully login!"

    def registerUser(self, username, password):
        if (self.db.check_user_exists(username) != None):
            return "User already exists"
        if (self.current_user != None):
            return "Already logged in, cannot register user!"
        userObj = self.db.register_user_in_database(username, password)
        # Create user home directory 
        outparams = self.file_manager.createDirectory(username)
        file_name_hash = self.file_manager.generateIntergityCodeForDirectory(outparams[0])
        self.db.create_home_dir(outparams[2], 
                        outparams[0], 
                        outparams[3], 
                        userObj, 
                        file_name_hash=file_name_hash)
        return "User registered!"

    def createFile(self, filename):
        if self.current_user == None:
            return "Must be logged in!"
        lookup_table = self.db.generate_rw_lookup_table(self.current_user)
        general_lookup_table = self.db.generate_general_lookup_table()
        enc_file_list = self.file_manager.getFileListInCurrentDir(general_lookup_table)
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
            if dec_file == filename:
                return "File already exists"
        havePermission = False
        enc_parent_path = ""
        for enc_path in lookup_table:
                dec_path = self.file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
                if dec_path == self.file_manager.current_path:
                    havePermission = True
                    enc_parent_path = enc_path
                    break
        if (not havePermission):
            return "Do not have permission to do that command"
        outputparams = self.file_manager.createFile(filename)
        file_name_hash, file_hash = self.file_manager.generateIntegrityCode(outputparams[0], outputparams[0])
        self.db.create_file(outputparams[2], 
                    outputparams[0], 
                    outputparams[3], 
                    self.current_user, 
                    False,
                    enc_parent_path,
                    file_name_hash,
                    file_hash)
        return "File created!"

    def deleteFile(self, filename):
        if self.current_user == None:
            return "Must be logged in!"
        general_lookup_table = self.db.generate_general_lookup_table()
        lookup_table = self.db.generate_rw_lookup_table(self.current_user)
        enc_file_list = self.file_manager.getFileListInCurrentDir(general_lookup_table)
        enc_file_name = ""
        fileExists = False
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
            if dec_file == filename:
                fileExists = True
                enc_file_name = enc_file_list[enc_file][1]
                break
        abs_path = os.path.join(self.file_manager.current_path, enc_file_name)
        if (not fileExists):
            return "File does not exist in current directory"
        havePermission = False
        enc_abs_path = ""
        for enc_path in lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
            if dec_path == abs_path:
                havePermission = True
                enc_abs_path = enc_path
                break
        if (not havePermission):
            return "Do not have permission to do that command"
        fileObj = self.db.check_file_exists(enc_abs_path)
        if (fileObj.is_home_dir):
            return "Cannot delete home directory"
        self.file_manager.deleteFile(filename, general_lookup_table)
        self.db.delete_file(fileObj)
        return "File deleted"

    def displayContents(self, filename):
        if self.current_user == None:
            return "Must be logged in!"
        enc_file_name = ""
        fileExists = False
        general_lookup_table = self.db.generate_general_lookup_table()
        lookup_table = self.db.generate_rw_lookup_table(self.current_user)
        enc_file_list = self.file_manager.getFileListInCurrentDir(general_lookup_table)
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
            if dec_file == filename:
                fileExists = True
                enc_file_name = enc_file_list[enc_file][1]
                break
        if (not fileExists):
            return "File does not exist in current directory"
        abs_path = os.path.join(self.file_manager.current_path, enc_file_name)
        enc_abs_path = ""
        havePermission = False
        for enc_path in lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
            if dec_path == abs_path:
                havePermission = True
                enc_abs_path = enc_path
                break
        if (not havePermission):
            return "Do not have permission to run this command"
        fileObj = self.db.check_file_exists(enc_abs_path)
        if (fileObj.is_dir):
            return "Is a directory, cannot display!"
        ans = self.file_manager.displayFileContents(filename, lookup_table)
        if ans == '':
            return '\n'
        return self.file_manager.displayFileContents(filename, lookup_table)

    def editFile(self, filename, contents):
        if self.current_user == None:
            return "Must be logged in!"
        general_lookup_table = self.db.generate_general_lookup_table()
        lookup_table = self.db.generate_rw_lookup_table(self.current_user)
        enc_file_list = self.file_manager.getFileListInCurrentDir(general_lookup_table)
        enc_file_name = ""
        fileExists = False
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
            if dec_file == filename:
                fileExists = True
                enc_file_name = enc_file_list[enc_file][1]
                break
        abs_path = os.path.join(self.file_manager.current_path, enc_file_name)
        if (not fileExists):
            return "File does not exist in current directory"
        havePermission = False
        enc_abs_path = ""
        for enc_path in lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
            if dec_path == abs_path:
                havePermission = True
                enc_abs_path = enc_path
                break
        if (not havePermission):
            return "Do not have permission to do that command"
        fileObj = self.db.check_file_exists(enc_abs_path)
        if (fileObj.is_dir):
            return "Cannot edit a directory"
        self.file_manager.addFileContentsWrapper(filename, general_lookup_table, contents)
        file_name_hash, file_hash = self.file_manager.generateIntegrityCode(enc_file_name, enc_file_name)
        self.db.edit_file(fileObj, enc_abs_path, enc_file_name, file_name_hash, file_hash)
        return "File edited!"

    def createDirectory(self, directoryname):
        if self.current_user == None:
            return "Must be logged in!"
        lookup_table = self.db.generate_rw_lookup_table(self.current_user)
        general_lookup_table = self.db.generate_general_lookup_table()
        enc_file_list = self.file_manager.getFileListInCurrentDir(general_lookup_table)
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
            if dec_file == directoryname:
                return "Directory already exists"
        havePermission = False
        enc_parent_path = ""
        for enc_path in lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
            if dec_path == self.file_manager.current_path:
                havePermission = True
                enc_parent_path = enc_path
                break
        if (not havePermission):
            return "Do not have permission to do that command"
        outputparams = self.file_manager.createDirectory(directoryname)
        file_name_hash = self.file_manager.generateIntergityCodeForDirectory(outputparams[0])
        self.db.create_file(outputparams[2], 
                    outputparams[0], 
                    outputparams[3], 
                    self.current_user, 
                    True, 
                    enc_parent_path,
                    file_name_hash=file_name_hash)
        return "Directory created!"

    def changeDirectory(self, directoryname):
        if self.current_user == None:
            return "Must be logged in!"
        if (directoryname == "../"):
            self.file_manager.changeDirectory(directoryname, {})
            return "Current directory: " + self.file_manager.relative_path
        fileExists = False
        access_lookup_table = self.db.generate_access_lookup_table(self.current_user)
        general_lookup_table = self.db.generate_general_lookup_table()
        enc_file_list = self.file_manager.getFileListInCurrentDir(general_lookup_table)
        enc_dir_name = ""
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
            if dec_file == directoryname:
                fileExists = True
                enc_dir_name = enc_file_list[enc_file][1]
                break
        if (not fileExists):
            return "Directory does not exist in current directory"
        havePermission = False
        enc_abs_path = ""
        abs_path = os.path.join(self.file_manager.current_path, enc_dir_name)
        for enc_path in access_lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, access_lookup_table[enc_path][0])
            if dec_path == abs_path:
                havePermission = True
                enc_abs_path = enc_path
                break
        if (not havePermission):
            return "Do not have permission to do that command"
        dirObj = self.db.check_file_exists(enc_abs_path)
        if (not dirObj.is_dir):
            return "Requested directory is not a directory"
        lookup_table_dir = {}
        lookup_table_dir[directoryname] = dirObj.file_name
        self.file_manager.changeDirectory(directoryname, lookup_table_dir)
        return  "Current directory: " + self.file_manager.relative_path

    def displayDirectoryContent(self):
        if self.current_user == None:
            return "Must be logged in!"
        lookup_table = self.db.generate_general_lookup_table()
        permitted_lookup_table = self.db.generate_rw_lookup_table(self.current_user)
        # at root, allow users to see directories
        if self.file_manager.current_path == self.file_manager.home_path:
            returnStr = ""
            for file in self.file_manager.listDir(lookup_table):
                returnStr += file + "\n"
            return returnStr[:-1]
        havePermission = False
        for enc_path in permitted_lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, permitted_lookup_table[enc_path][0])
            if dec_path == self.file_manager.current_path:
                enc_abs_path = enc_path
                havePermission = True
                break
        # do not have r/w permissions for the current dir, display all contents as encrypted
        if (not havePermission):
            returnStr = ""
            for file in os.listdir():
                returnStr += file + "\n"
            return returnStr[:-1]
        returnStr = ""
        for file in self.file_manager.listDir(lookup_table):
            returnStr += file + "\n"
        return returnStr[:-1]

    def renameFile(self, old_file_name, new_file_name):
        if self.current_user == None:
            return "Must be logged in!"
        fileExists = False
        lookup_table = self.db.generate_rw_lookup_table(self.current_user)
        general_lookup_table = self.db.generate_general_lookup_table()
        enc_file_list = self.file_manager.getFileListInCurrentDir(general_lookup_table)
        enc_old_file_name = ""
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
            if dec_file == old_file_name:
                enc_old_file_name = enc_file_list[enc_file][1]
                fileExists = True
                break
        if (not fileExists):
            return "File does not exist in current directory"
        havePermission = False
        abs_path = os.path.join(self.file_manager.current_path, enc_old_file_name)
        enc_old_abs_path = ""
        for enc_path in lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
            if dec_path == abs_path:
                havePermission = True
                enc_old_abs_path = enc_path
                break
        if (not havePermission):
            return "Do not have permission to do that command"
        fileObj = self.db.check_file_exists(enc_old_abs_path)
        if (fileObj.is_home_dir):
            return "Cannot rename home directory of user"
        outparams = self.file_manager.renameFile_public(old_file_name, lookup_table, new_file_name)
        if (fileObj.is_dir):
            file_name_hash = self.file_manager.generateIntegrityCodeForDirectory(outparams[0])        
        else:
            file_name_hash, file_hash =  self.file_manager.generateIntegrityCode(outparams[0], outparams[0])
        self.db.rename_file(fileObj, outparams[2], outparams[0], file_name_hash)  
        return "File " + old_file_name + " renamed to " + new_file_name

    def changePermissionMode(self, filename, permission_mode):
        if self.current_user == None:
            return "Must be logged in to run command!"
        gen_lookup_table = self.db.generate_general_lookup_table()
        lookup_table = self.db.generate_owned_lookup_table(self.current_user)
        enc_file_list = self.file_manager.getFileListInCurrentDir(gen_lookup_table)
        enc_file_name = ""
        fileExists = False
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
            if dec_file == filename:
                fileExists = True
                enc_file_name = enc_file_list[enc_file][1]
                break
        if (not fileExists):
            return "File does not exist in current directory"
        enc_abs_path = ""
        abs_path = os.path.join(self.file_manager.current_path, enc_file_name)
        havePermission = False
        for enc_path in lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
            if dec_path == abs_path:
                havePermission = True
                enc_abs_path = enc_path
                break
        if (not havePermission):
            return "Do not have permission to do that command"
        fileObj = self.db.check_file_exists(enc_abs_path)
        if (not self.db.set_permission_mode(fileObj, permission_mode)):
            return "Permission could not be changed"
        return "Permission changed"

    def checkIntergityOfFiles(self):
        if self.current_user == None:
            return None
        lookup_table = self.db.generate_owned_lookup_table(self.current_user)
        comprisedFiles = []
        for enc_path in lookup_table:
            fileObj = self.db.check_file_exists(enc_path)
            dec_path = self.file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
            if (fileObj.is_dir):
                if (not self.file_manager.verifyIntergityCodeForDirectory(dec_path)):
                    comprisedFiles.append(fileObj)
            else:
                if (not self.file_manager.verifyIntegrityCode(dec_path, lookup_table[enc_path][1], fileObj.file_name_hash, fileObj.file_hash)):
                    comprisedFiles.append(fileObj)
        return comprisedFiles

    def logout(self):
        self.current_user = None
        self.file_manager.resetToHomePath()
        returnStr = self.file_manager.relative_path
        return "Current directory: " + returnStr + "\nLogged out"

    def getPlainTextFilePaths(self, file_list):
        generalLookupTable = self.db.generate_general_lookup_table()
        plainAbsPaths = []
        for file in file_list:
            for enc_path in generalLookupTable:
                if enc_path == file.abs_path:
                    dec_path = self.file_manager.DecryptFileName(enc_path, generalLookupTable[enc_path][0])
                    plainAbsPaths.append(self.getPlainTextFilePath(dec_path))
        return plainAbsPaths

    def getPlainTextFilePath(self,dec_path):
        dec_relative_path = os.path.join('/home', os.path.relpath(dec_path, self.file_manager.home_path))
        pathArray = dec_relative_path.split("/")
        fileLookup = self.db.generate_file_lookup_table()
        cleanedPathArr = []
        for pathEle in pathArray[2:]:
            dec_file = self.file_manager.DecryptFileName(pathEle, fileLookup[pathEle])
            cleanedPathArr.append(dec_file)
        cleaned_path = "/home"
        for cleanedPathEle in cleanedPathArr:
            cleaned_path += "/" + cleanedPathEle
        return cleaned_path
    
    def createGroup(self,groupname):
        if self.db.check_group_exists(groupname) != None:
            return "Group already exists"
        self.db.create_group_in_database(groupname)
        return "Group successfuly registered"

    def addUserToGroup(self,username, groupname):
        user = self.db.check_user_exists(username)
        group = self.db.check_group_exists(groupname)
        if user == None:
            return "Specified user does not exist"
        if group == None:
            return "Specified group does not exist"
        if not self.db.add_user_to_group(user, group):
            return "User already exists in group"
        return "User added to group"

def main():
    server = Server(HOST, PORT)
    try:
        server.start_server()
    except:
        server.close_server()
        traceback.print_exc()

if __name__ == "__main__": 
    main()
    