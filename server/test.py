import database_manager
import file_manager
import os

db = database_manager.DatabaseManager()
current_user = None
file_manager = file_manager.FileManager()

# Test debugger to test server, treat this as a server side client, you input commands
# and arguments and the system will execute them

# logout - lets you log out

# Special command:
#   reset - this will clear and reset the database
# NOTE: need to delete home_dir whenever restarting, this will need to be fixed
# NOTE: hash and file intergity not implemented yet

# Test cases:
# 1) Create a user "jasonk" with password "pass" with the "register" command
#   Expected output: User is created, and directory for jasonk is created in home_dir
# 2) Create a user "jasonk" with any password "register"
#   Expected output: User is already created, no new directory created
# 3) Log in to user "jasonk" with an incorrect password
#   Expected output: Incorrect password, not logged in
# 4) Log in to user "jasonk" with correct password
#   Expected output: Logged in
# 5) Log in when already logged in
#   Expected output: Already logged in
# 6) Navigate into directory called "jasonk"
#   Expected output: Navigated into jasonk
# 7) Create file named "1.txt"
#   Expected output: File created
# 8) Create file named "1.txt"
#   Expected output: File already exists
# 9) Add file contents to "1.txt" 
#   Expected output: Contents added to 1.txt
# 10) Display file contents of "1.txt"
#   Expected output: Plaintext content of 1.txt
# 11) Display directory contents
#   Expected output: Should see one file, "1.txt", in plain text
# 12) Rename file "1.txt" to "2.txt"
#   Expected output: File renamed

def main():
    while True:
        command = input("Enter command: ")
        commandArr = command.split()
        if (commandArr[0] == "login"):
            print(login(commandArr[1], commandArr[2]))
        elif (commandArr[0] == "register"):
            print(registerUser(commandArr[1], commandArr[2]))
        elif (commandArr[0] == "createGroup"):
            print(createGroup(commandArr[1]))
        elif (commandArr[0] == "createFile"):
            print(createFile(commandArr[1]))
        elif (commandArr[0] == "addUserToGroup"):
            print(addUserToGroup(commandArr[1]))
        elif (commandArr[0] == "displayFile"):
            print(displayContents(commandArr[1]))
        elif(commandArr[0] == "addFileContents"):
            print(editFile(commandArr[1], commandArr[2]))
        elif (commandArr[0] == "createDirectory"):
            print(createDirectory(commandArr[1]))
        elif (commandArr[0] == "changeDirectory"):
            print(changeDirectory(commandArr[1]))
        elif (commandArr[0] == "displayDirectoryContents"):
            print(displayDirectoryContent())
        elif(commandArr[0] == "renameFile"):
            print(renameFile(commandArr[1], commandArr[2]))
        elif(commandArr[0] == "grantPermission"):
            print(grantPermission(commandArr[1], commandArr[2]))
        elif(commandArr[0] == "removePermission"):
            print(removePermission(commandArr[1], commandArr[2]))
        elif(commandArr[0] == "reset"):
            reset_database()
        elif (commandArr[0] == "logout"):
            logout()
        
def reset_database():
    db.drop_tables()
    db.create_tables()

def set_up_database():
    db.create_tables()

def login(username, password):
    global current_user
    if current_user != None:
        return "Already logged in!"
    user_obj = db.check_user_exists(username)
    if user_obj == None:
        return "User does not exist"
    if not db.login_in_user(username, password):
        return "Password does not match"
    current_user = user_obj
    return "Successfully login!"

def registerUser(username, password):
    if (db.check_user_exists(username) != None):
        return "User already exists"
    userObj = db.register_user_in_database(username, password)
    outparams = file_manager.createDirectory(username)
    db.create_file(outparams[2], outparams[0], outparams[3], userObj, True)
    return "User registered!"

def createGroup(groupname):
    if db.check_group_exists(groupname) != None:
        return "Group already exists"
    db.create_group_in_database(groupname)
    return "Group successfuly registered"

def addUserToGroup(username, groupname):
    user = db.check_user_exists(username)
    group = db.check_group_exists(groupname)
    if user == None:
        return "Specified user does not exist"
    if group == None:
        return "Specified group does not exist"
    db.add_user_to_group(user, group)

def createFile(filename):
    if current_user == None:
        return "Must be logged in!"
    lookup_table = db.generate_permitted_lookup_table(current_user)
    group_lookup_table = db.generate_group_permitted_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(group_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file[1],(enc_file[0]))
        if dec_file == filename:
            return "File already exists"
    havePermission = False
    for enc_path in lookup_table:
            dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
            if dec_path == file_manager.current_path:
                havePermission = True
                break
    if (not havePermission):
        return "Do not have permission to do that command"
    outputparams = file_manager.createFile(filename)
    # TO DO: add file hash to parameters
    db.create_file(outputparams[2], outputparams[0], outputparams[3], current_user, False)
    return "File created!"

def displayContents(filename):
    if current_user == None:
        return "Must be logged in!"
    abs_path = os.path.join(file_manager.current_path, filename)
    fileExists = False
    group_lookup_table = db.generate_group_permitted_lookup_table(current_user)
    lookup_table = db.generate_permitted_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(group_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file[1], enc_file[0])
        if dec_file == filename:
            fileExists = True
            break
    if (not fileExists):
        return "File does not exist in current directory"
    havePermission = False
    enc_abs_path = ""
    for enc_path in lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
        if dec_path == abs_path:
            havePermission = True
            enc_abs_path = enc_path
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    return file_manager.displayFileContents(filename, lookup_table)


def editFile(filename, contents):
    if current_user == None:
        return "Must be logged in!"
    abs_path = os.path.join(file_manager.current_path, filename)
    group_lookup_table = db.generate_group_permitted_lookup_table(current_user)
    lookup_table = db.generate_permitted_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(group_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file[1], enc_file[0])
        if dec_file == filename:
            fileExists = True
            break
    if (not fileExists):
        return "File does not exist in current directory"
    havePermission = False
    enc_abs_path = ""
    for enc_path in lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
        if dec_path == abs_path:
            havePermission = True
            enc_abs_path = enc_path
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    # TO DO: need hash support
    file_manager.addFileContentsWrapper(filename, group_lookup_table, contents)
    return "File edited!"


def createDirectory(directoryname):
    if current_user == None:
        return "Must be logged in!"
    lookup_table = db.generate_permitted_lookup_table(current_user)
    group_lookup_table = db.generate_group_permitted_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(group_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file[1], enc_file[0])
        if dec_file == directoryname:
            return "Directory already exists"
        havePermission = False
    for enc_path in lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
        if dec_path == file_manager.current_path:
            havePermission = True
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    outputparams = file_manager.createDirectory(directoryname)
    db.create_file(outputparams[2], outputparams[0], outputparams[3], current_user, True)
    return "Directory created!"

def changeDirectory(directoryname):
    if current_user == None:
        return "Must be logged in!"
    if (directoryname == "../"):
        file_manager.changeDirectory(directoryname)
    abs_path = os.path.join(file_manager.current_path, directoryname)
    fileExists = False
    group_lookup_table = db.generate_group_permitted_lookup_table(current_user)
    print("Lookup table " + str(group_lookup_table))
    enc_file_list = file_manager.getFileListInCurrentDir(group_lookup_table)
    print("File list: " + str(enc_file_list))
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file[1], enc_file[0])
        if dec_file == directoryname:
            fileExists = True
            break
    if (not fileExists):
        return "Directory does not exist in current directory"
    havePermission = False
    for enc_path in group_lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, group_lookup_table[enc_path][0])
        if dec_path == abs_path:
            enc_abs_path = enc_path
            havePermission = True
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    dirObj = db.check_file_exists(enc_abs_path)
    if (not dirObj.is_dir):
        return "Requested directory is not a directory"
    file_manager.changeDirectory(directoryname)
    return file_manager.relative_path

def displayDirectoryContent():
    if current_user == None:
        return "Must be logged in!"
    group_lookup_table = db.generate_group_permitted_lookup_table(current_user)
    havePermission = False
    for enc_path in group_lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, group_lookup_table[enc_path][0])
        if dec_path == file_manager.current_path:
            enc_abs_path = enc_path
            havePermission = True
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    return file_manager.listDir(group_lookup_table)

def renameFile(old_file_name, new_file_name):
    if current_user == None:
        return "Must be logged in!"
    abs_path = os.path.join(file_manager.current_path, old_file_name)
    fileExists = False
    lookup_table = db.generate_permitted_lookup_table(current_user)
    group_lookup_table = db.generate_group_permitted_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(group_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file[1], enc_file[0])
        if dec_file == old_file_name:
            fileExists = True
            break
    if (not fileExists):
        return "File does not exist in current directory"
    enc_abs_path = ""
    for enc_path in lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
        if dec_path == abs_path:
            havePermission = True
            enc_abs_path = enc_path
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    outparams = file_manager.renameFile_public(old_file_name, lookup_table, new_file_name)
    fileObj = db.check_file_exists(outparams[3])
    db.rename_file(fileObj, outparams[2], outparams[0])
    return "File " + old_file_name + "renamed to " + new_file_name

    
def grantPermission(username, filename):
    if current_user == None:
        return "Must be logged in!"
    userObj = db.check_user_exists(username)
    if (userObj == None):
        return "Specified user does not exist"
    abs_path = os.path.join(file_manager.current_path, filename)
    group_lookup_table = db.generate_group_permitted_lookup_table(current_user)
    lookup_table = db.generate_owned_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(group_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file[1], enc_file[0])
        if dec_file == filename:
            fileExists = True
            break
    if (not fileExists):
        return "File does not exist in current directory"
    enc_abs_path = ""
    for enc_path in lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
        if dec_path == abs_path:
            havePermission = True
            enc_abs_path = enc_path
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    fileObj = db.check_file_exists(enc_abs_path)
    if (not db.grant_permissions(fileObj, userObj)):
        return "User already has permission to that file"
    return "Permission granted!"

def removePermission(username, filename):
    if current_user == None:
        return "Must be logged in!"
    userObj = db.check_user_exists(username)
    if (userObj == None):
        return "Specified user does not exist"
    abs_path = os.path.join(file_manager.current_path, filename)
    group_lookup_table = db.generate_group_permitted_lookup_table(current_user)
    lookup_table = db.generate_owned_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(group_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file[1], enc_file[0])
        if dec_file == filename:
            fileExists = True
            break
    if (not fileExists):
        return "File does not exist in current directory"
    enc_abs_path = ""
    for enc_path in lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
        if dec_path == abs_path:
            havePermission = True
            enc_abs_path = enc_path
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    fileObj = db.check_file_exists(enc_abs_path)
    returnedTuple =  db.grant_permissions(fileObj, userObj)[0]
    if (not returnedTuple[0]):
        return returnedTuple[1]
    return "Permission removed!"

def logout():
    global current_user
    current_user = None
    return "Logged out"


if __name__ == "__main__":
    main()