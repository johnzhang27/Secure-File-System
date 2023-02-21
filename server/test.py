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
            print(addUserToGroup(commandArr[1], commandArr[2]))
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
    print(changeDirectory(current_user.user_id))
    compFiles = checkIntergityOfFiles()
    if (compFiles != None):
        print("The following files have been changed since your last login: ")
        for file in getPlainTextFilePaths(compFiles):
            print(file)
    return "Successfully login!"

def registerUser(username, password):
    global current_user
    if (db.check_user_exists(username) != None):
        return "User already exists"
    if (current_user != None):
        return "Already logged in, cannot register user!"
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
    general_lookup_table = db.generate_general_lookup_table()
    enc_file_list = file_manager.getFileListInCurrentDir(general_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
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
    file_name_hash, file_hash = file_manager.generateIntegrityCode(outputparams[0])
    db.create_file(outputparams[2], 
                   outputparams[0], 
                   outputparams[3], 
                   current_user, 
                   False,
                   file_name_hash,
                   file_hash)
    return "File created!"

def displayContents(filename):
    if current_user == None:
        return "Must be logged in!"
    enc_file_name = ""
    fileExists = False
    general_lookup_table = db.generate_general_lookup_table()
    lookup_table = db.generate_permitted_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(general_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
        if dec_file == filename:
            fileExists = True
            enc_file_name = enc_file_list[enc_file][1]
            break
    if (not fileExists):
        return "File does not exist in current directory"
    abs_path = os.path.join(file_manager.current_path, enc_file_name)
    enc_abs_path = ""
    havePermission = False
    for enc_path in lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
        if dec_path == abs_path:
            havePermission = True
            enc_abs_path = enc_path
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    fileObj = db.check_file_exists(enc_abs_path)
    if (fileObj.is_dir):
        return "Is a directory, cannot display!"
    return file_manager.displayFileContents(filename, lookup_table)


def editFile(filename, contents):
    if current_user == None:
        return "Must be logged in!"
    general_lookup_table = db.generate_general_lookup_table()
    lookup_table = db.generate_permitted_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(general_lookup_table)
    enc_file_name = ""
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
        if dec_file == filename:
            fileExists = True
            enc_file_name = enc_file_list[enc_file][1]
            break
    abs_path = os.path.join(file_manager.current_path, enc_file_name)
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
    file_manager.addFileContentsWrapper(filename, general_lookup_table, contents)
    file_name_hash, file_hash = file_manager.generateIntegrityCode(enc_file_name)
    fileObj = db.check_file_exists(enc_abs_path)
    db.edit_file(fileObj, enc_abs_path, enc_file_name, file_name_hash, file_hash)
    return "File edited!"

def createDirectory(directoryname):
    if current_user == None:
        return "Must be logged in!"
    lookup_table = db.generate_permitted_lookup_table(current_user)
    general_lookup_table = db.generate_general_lookup_table()
    enc_file_list = file_manager.getFileListInCurrentDir(general_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
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
        file_manager.changeDirectory(directoryname, {})
        return file_manager.relative_path
    fileExists = False
    group_lookup_table = db.generate_group_permitted_lookup_table(current_user)
    general_lookup_table = db.generate_general_lookup_table()
    enc_file_list = file_manager.getFileListInCurrentDir(general_lookup_table)
    enc_dir_name = ""
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
        if dec_file == directoryname:
            fileExists = True
            enc_dir_name = enc_file_list[enc_file][1]
            break
    if (not fileExists):
        return "Directory does not exist in current directory"
    havePermission = False
    enc_abs_path = ""
    abs_path = os.path.join(file_manager.current_path, enc_dir_name)
    for enc_path in group_lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, group_lookup_table[enc_path][0])
        if dec_path == abs_path:
            havePermission = True
            enc_abs_path = enc_path
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    dirObj = db.check_file_exists(enc_abs_path)
    if (not dirObj.is_dir):
        return "Requested directory is not a directory"
    lookup_table_dir = {}
    lookup_table_dir[directoryname] = dirObj.file_name
    file_manager.changeDirectory(directoryname, lookup_table_dir)
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
    fileExists = False
    lookup_table = db.generate_permitted_lookup_table(current_user)
    general_lookup_table = db.generate_general_lookup_table()
    enc_file_list = file_manager.getFileListInCurrentDir(general_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
        if dec_file == old_file_name:
            enc_old_file_name = enc_file_list[enc_file][1]
            fileExists = True
            break
    if (not fileExists):
        return "File does not exist in current directory"
    havePermission = False
    abs_path = os.path.join(file_manager.current_path, enc_old_file_name)
    enc_old_abs_path = ""
    for enc_path in lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
        if dec_path == abs_path:
            havePermission = True
            enc_old_abs_path = enc_path
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    outparams = file_manager.renameFile_public(old_file_name, lookup_table, new_file_name)
    fileObj = db.check_file_exists(enc_old_abs_path)
    db.rename_file(fileObj, outparams[2], outparams[0])
    return "File " + old_file_name + "renamed to " + new_file_name

def grantPermission(username, filename):
    if current_user == None:
        return "Must be logged in!"
    userObj = db.check_user_exists(username)
    if (userObj == None):
        return "Specified user does not exist"
    general_lookup_table = db.generate_general_lookup_table()
    lookup_table = db.generate_owned_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(general_lookup_table)
    enc_file_name = ""
    fileExists = False
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
        if dec_file == filename:
            fileExists = True
            enc_file_name = enc_file_list[enc_file][1]
            break
    if (not fileExists):
        return "File does not exist in current directory"
    abs_path = os.path.join(file_manager.current_path, enc_file_name)
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
    general_lookup_table = db.generate_general_lookup_table()
    lookup_table = db.generate_owned_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(general_lookup_table)
    enc_file_name = ""
    fileExists = False
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
        if dec_file == filename:
            fileExists = True
            enc_file_name = enc_file_list[enc_file][1]
            break
    if (not fileExists):
        return "File does not exist in current directory"
    enc_abs_path = ""
    abs_path = os.path.join(file_manager.current_path, enc_file_name)
    for enc_path in lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path,  lookup_table[enc_path][0])
        if dec_path == abs_path:
            havePermission = True
            enc_abs_path = enc_path
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    fileObj = db.check_file_exists(enc_abs_path)
    returnedTuple =  db.remove_permissions(fileObj, userObj)
    if (not returnedTuple[0]):
        return returnedTuple[1]
    return "Permission removed!"

def checkIntergityOfFiles():
    global current_user
    if current_user == None:
        return None
    lookup_table = db.generate_owned_lookup_table(current_user)
    comprisedFiles = []
    for enc_path in lookup_table:
        fileObj = db.check_file_exists(enc_path)
        if (fileObj.is_dir):
            continue
        dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
        if (not file_manager.verifyIntegrityCode(dec_path, fileObj.file_name_hash, fileObj.file_hash)):
            comprisedFiles.append(fileObj)
    return comprisedFiles

def logout():
    global current_user
    current_user = None
    file_manager.resetToHomePath()
    print(file_manager.relative_path)
    return "Logged out"

def getPlainTextFilePaths(file_list):
    generalLookupTable = db.generate_general_lookup_table()
    plainAbsPaths = []
    for file in file_list:
        for enc_path in generalLookupTable:
            if enc_path == file.abs_path:
                dec_path = file_manager.DecryptFileName(enc_path, generalLookupTable[enc_path][0])
                plainAbsPaths.append(getPlainTextFilePath(dec_path))
    return plainAbsPaths

def getPlainTextFilePath(dec_path):
    dec_relative_path = os.path.join('\\home', os.path.relpath(dec_path, file_manager.home_path))
    pathArray = dec_relative_path.split("\\")
    fileLookup = db.generate_file_lookup_table()
    cleanedPathArr = []
    for pathEle in pathArray[2:]:
        dec_file = file_manager.DecryptFileName(pathEle, fileLookup[pathEle])
        cleanedPathArr.append(dec_file)
    cleaned_path = "\\home"
    for cleanedPathEle in cleanedPathArr:
        cleaned_path += "\\" + cleanedPathEle
    return cleaned_path

    



if __name__ == "__main__":
    main()