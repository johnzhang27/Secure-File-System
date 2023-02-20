import socket
import sys
import os
import database_manager
import file_manager
import sqlalchemy

# https://docs.sqlalchemy.org/en/20/tutorial/engine.html
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html
# https://docs.sqlalchemy.org/en/20/core/engines.html

HOST = "127.0.0.1"
PORT = 8000

# TO DO: encrypting usernames and password

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
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.listen()
        while True: 
            conn, addr = self.socket.accept()
            self.handle_request(conn)

    def close_server(self):
        self.socket.close()
        self.db.close_session()

    def handle_request(self, conn):
        with conn:
            rec_data = b""
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                rec_data += data
        self.parse_rec_data(rec_data, conn)
    
    def parse_rec_data(self, rec_data, conn):
        rec_string = rec_data.decode()
        recStringArray = rec_string.split()
        commandCode = 0
        try:
            commandCode = int(recStringArray[0])
        except ValueError:
            #send error response: improper command
            conn.sendall("Improper command")
            return
        if (commandCode == 0):
            if len(recStringArray) != 3:
                 #send error response: improper command
                conn.sendall("Improper command")
                return
            conn.sendall(self.login(recStringArray[1], recStringArray[2]))
        elif (commandCode == 1):
            if len(recStringArray) != 3:
                 #send error response: improper command
                conn.sendall("Improper command")
                return
            conn.sendall(self.registerUser(recStringArray[1], recStringArray[2]))
        elif (commandCode == 2):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command")
                return 
            conn.sendall(self.createFile(recStringArray[1]))
        elif (commandCode == 3):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command")
                return
            conn.sendall(self.displayContents(recStringArray[1]))
        elif (commandCode == 4):
            if len(recStringArray) != 3:
                 #send error response: improper command
                conn.sendall("Improper command")
                return
            conn.sendall(self.editFile(recStringArray[1], recStringArray[2]))
        elif (commandCode == 5):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command")
                return
            conn.sendall(self.createDirectory(recStringArray[1]))
        elif (commandCode == 6):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command")
                return
            conn.sendall(self.changeDirectory(recStringArray[1]))
        elif (commandCode == 7):
            if len(recStringArray) != 1:
                 #send error response: improper command
                conn.sendall("Improper command")
                return
            conn.sendall(self.displayDirectoryContent())
        elif (commandCode == 8):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command")
                return
            conn.sendall(self.renameFile(recStringArray[1], recStringArray[2]))
        elif (commandCode == 9):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command")
                return
            conn.sendall(self.grantPermission(recStringArray[1], recStringArray[2]))
        elif (commandCode == 10):
            if len(recStringArray) != 2:
                 #send error response: improper command
                conn.sendall("Improper command")
                return
            conn.sendall(self.removePermission(recStringArray[1], recStringArray[2]))
        else:
            conn.sendall("Improper command")
            return

    def login(self, username, password):
        if self.current_user != None:
            return "Already logged in"
        user_obj = self.db.check_user_exists(username)
        if user_obj == None:
            return "User does not exist"
        if not self.db.login_in_user(username, password):
            return "Password does not match"
        self.current_user = user_obj
        return "Successfully login!"

    def registerUser(self, username, password):
        if (self.db.check_user_exists(username) != None):
            return "User already exists"
        userObj = self.db.register_user_in_database(username, password)
        # Creating home dir for user
        outparams = self.file_manager.createDirectory(username)
        self.db.create_file(outparams[2], outparams[0], outparams[3], userObj, True)
        return "User registered!"

    def createFile(self, filename):
        if self.current_user == None:
            return "Must be logged in to run command!"
        lookup_table = self.db.generate_permitted_lookup_table(self.current_user)
        group_lookup_table = self.db.generate_group_permitted_lookup_table(self.current_user)
        enc_file_list = self.file_manager.getFileListInCurrentDir(group_lookup_table)
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file[1], enc_file[0])
            if dec_file == filename:
                return "File already exists"
        havePermission = False
        for enc_path in lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
            if dec_path == self.file_manager.current_path:
                havePermission = True
                break
        if (not havePermission):
            return "Do not have permission to do that command"
        outputparams = self.file_manager.createFile(filename)
        # TO DO: add file hash to parameters
        self.db.create_file(outputparams[2], outputparams[0], outputparams[3], self.current_user, False)
        return "File created!"

    def displayContents(self, filename):
        if self.current_user == None:
            return "Must be logged in to run command!"
        abs_path = os.path.join(self.file_manager.current_path, filename)
        fileExists = False
        group_lookup_table = self.db.generate_group_permitted_lookup_table(self.current_user)
        lookup_table = self.db.generate_permitted_lookup_table(self.current_user)
        enc_file_list = self.file_manager.getFileListInCurrentDir(group_lookup_table)
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file[1], enc_file[0])
            if dec_file == filename:
                fileExists = True
                break
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
        return self.file_manager.displayFileContents(filename, lookup_table)

    
    def editFile(self, filename, contents):
        if self.current_user == None:
            return "Must be logged in to run command!"
        abs_path = os.path.join(self.file_manager.current_path, filename)
        group_lookup_table = self.db.generate_group_permitted_lookup_table(self.current_user)
        lookup_table = self.db.generate_permitted_lookup_table(self.current_user)
        enc_file_list = self.file_manager.getFileListInCurrentDir(group_lookup_table)
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file[1], enc_file[0])
            if dec_file == filename:
                fileExists = True
                break
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
        # TO DO: need hash support
        self.file_manager.addFileContentsWrapper(filename, group_lookup_table, contents)
        return "File edited!"

    
    def createDirectory(self, directoryname):
        if self.current_user == None:
            return "Must be logged in to run command!"
        lookup_table = self.db.generate_permitted_lookup_table(self.current_user)
        group_lookup_table = self.db.generate_group_permitted_lookup_table(self.current_user)
        enc_file_list = self.file_manager.getFileListInCurrentDir(group_lookup_table)
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file[1], enc_file[0])
            if dec_file == directoryname:
                return "Directory already exists"
            havePermission = False
        for enc_path in lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
            if dec_path == self.file_manager.current_path:
                havePermission = True
                break
        if (not havePermission):
            return "Do not have permission to do that command"
        outputparams = self.file_manager.createDirectory(directoryname)
        self.db.create_file(outputparams[2], outputparams[0], outputparams[3], self.current_user, True)
        return "Directory created!"

    def changeDirectory(self, directoryname):
        if self.current_user == None:
            return "Must be logged in to run command!"
        if (directoryname == "../"):
            self.file_manager.changeDirectory(directoryname)
        abs_path = os.path.join(self.file_manager.current_path, directoryname)
        fileExists = False
        group_lookup_table = self.db.generate_group_permitted_lookup_table(self.current_user)
        enc_file_list = self.file_manager.getFileListInCurrentDir(group_lookup_table)
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file[1], enc_file[0])
            if dec_file == directoryname:
                fileExists = True
                break
        if (not fileExists):
            return "Directory does not exist in current directory"
        havePermission = False
        for enc_path in group_lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, group_lookup_table[enc_path][0])
            if dec_path == abs_path:
                enc_abs_path = enc_path
                havePermission = True
                break
        if (not havePermission):
            return "Do not have permission to do that command"
        dirObj = self.db.check_file_exists(enc_abs_path)
        if (not dirObj.is_dir):
            return "Requested directory is not a directory"
        self.file_manager.changeDirectory(directoryname)
        return self.file_manager.relative_path

    def displayDirectoryContent(self):
        if self.current_user == None:
            return "Must be logged in to run command!"
        group_lookup_table = self.db.generate_group_permitted_lookup_table(self.current_user)
        havePermission = False
        for enc_path in group_lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, group_lookup_table[enc_path][0])
            if dec_path == self.file_manager.current_path:
                enc_abs_path = enc_path
                havePermission = True
                break
        if (not havePermission):
            return "Do not have permission to do that command"
        return self.file_manager.listDir(group_lookup_table)

    def renameFile(self, old_file_name, new_file_name):
        if self.current_user == None:
            return "Must be logged in to run command!"
        abs_path = os.path.join(self,file_manager.current_path, old_file_name)
        fileExists = False
        lookup_table = self.db.generate_permitted_lookup_table(self.current_user)
        group_lookup_table = self.db.generate_group_permitted_lookup_table(self.current_user)
        enc_file_list = self.file_manager.getFileListInCurrentDir(group_lookup_table)
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file[1], enc_file[0])
            if dec_file == old_file_name:
                fileExists = True
                break
        if (not fileExists):
            return "File does not exist in current directory"
        enc_abs_path = ""
        for enc_path in lookup_table:
            dec_path = self.file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
            if dec_path == abs_path:
                havePermission = True
                enc_abs_path = enc_path
                break
        if (not havePermission):
            return "Do not have permission to do that command"
        outparams = self.file_manager.renameFile_public(old_file_name, lookup_table, new_file_name)
        fileObj = self.db.check_file_exists(outparams[3])
        self.db.rename_file(fileObj, outparams[2], outparams[0])
        return "File " + old_file_name + "renamed to " + new_file_name

        
    def grantPermission(self, username, filename):
        if self.current_user == None:
            return "Must be logged in to run command!"
        userObj = self.db.check_user_exists(username)
        if (userObj == None):
            return "Specified user does not exist"
        abs_path = os.path.join(self.file_manager.current_path, filename)
        group_lookup_table = self.db.generate_group_permitted_lookup_table(self.current_user)
        lookup_table = self.db.generate_owned_lookup_table(self.current_user)
        enc_file_list = self.file_manager.getFileListInCurrentDir(group_lookup_table)
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file[1], enc_file[0])
            if dec_file == filename:
                fileExists = True
                break
        if (not fileExists):
            return "File does not exist in current directory"
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
        if (not self.db.grant_permissions(fileObj, userObj)):
            return "User already has permission to that file"
        return "Permission granted!"

    def removePermission(self, username, filename):
        if self.current_user == None:
            return "Must be logged in to run command!"
        userObj = self.db.check_user_exists(username)
        if (userObj == None):
            return "Specified user does not exist"
        abs_path = os.path.join(self.file_manager.current_path, filename)
        group_lookup_table = self.db.generate_group_permitted_lookup_table(self.current_user)
        lookup_table = self.db.generate_owned_lookup_table(self.current_user)
        enc_file_list = self.file_manager.getFileListInCurrentDir(group_lookup_table)
        for enc_file in enc_file_list:
            dec_file = self.file_manager.DecryptFileName(enc_file[1], enc_file[0])
            if dec_file == filename:
                fileExists = True
                break
        if (not fileExists):
            return "File does not exist in current directory"
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
        returnedTuple =  self.db.grant_permissions(fileObj, userObj)[0]
        if (not returnedTuple[0]):
            return returnedTuple[1]
        return "Permission removed!"

    def checkIntergityOfFiles(self):
        if self.current_user == None:
            return None
        comprised_files = []
        for file in self.current_user.owned_files:
            # TO DO: compute file hash
            hash = ""
            # compare to hash stored in DB
            hash == file.hash
        return comprised_files

    def logout(self):
        self.current_user = None
        return "Logged out"

def main():
    server = Server(HOST, PORT)
    server.start_server()

if __name__ == "__main__":
    main()