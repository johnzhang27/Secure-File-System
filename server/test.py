import database_manager
import file_manager
import os

# Test debugger to test server, treat this as a server side client, you input commands
# and arguments and the system will execute them

# logout - lets you log out

# Special command:
#   reset - this will clear and reset the database

db = database_manager.DatabaseManager()
current_user = None
file_manager = file_manager.FileManager()

def main():
    while True:
        command = input("Enter command: ")
        commandArr = command.split()
        if (commandArr[0] == "login"):
            if (len(commandArr) != 3):
                print("Improper command")
                continue
            print(login(commandArr[1], commandArr[2]))
        elif (commandArr[0] == "register"):
            if (len(commandArr) != 3):
                print("Improper command")
                continue
            print(registerUser(commandArr[1], commandArr[2]))
        elif (commandArr[0] == "createGroup"):
            if (len(commandArr) != 2):
                print("Improper command")
                continue
            print(createGroup(commandArr[1]))
        elif (commandArr[0] == "createFile"):
            if (len(commandArr) != 2):
                print("Improper command")
                continue
            print(createFile(commandArr[1]))
        elif (commandArr[0] == "addUserToGroup"):
            if (len(commandArr) != 3):
                print("Improper command")
                continue
            print(addUserToGroup(commandArr[1], commandArr[2]))
        elif (commandArr[0] == "displayFile"):
            if (len(commandArr) != 2):
                print("Improper command")
                continue
            print(displayContents(commandArr[1]))
        elif(commandArr[0] == "addFileContents"):
            if (len(commandArr) != 3):
                print("Improper command")
                continue
            print(editFile(commandArr[1], commandArr[2]))
        elif (commandArr[0] == "createDirectory"):
            if (len(commandArr) != 2):
                print("Improper command")
                continue
            print(createDirectory(commandArr[1]))
        elif (commandArr[0] == "changeDirectory"):
            if (len(commandArr) != 2):
                print("Improper command")
                continue
            print(changeDirectory(commandArr[1]))
        elif (commandArr[0] == "displayDirectoryContents"):
            if (len(commandArr) != 1):
                print("Improper command")
                continue
            print(displayDirectoryContent())
        elif(commandArr[0] == "renameFile"):
            if (len(commandArr) != 3):
                print("Improper command")
                continue
            print(renameFile(commandArr[1], commandArr[2]))
        elif(commandArr[0] == "changeP"):
            if (len(commandArr) != 3):
                print("Improper command")
                continue
            print(changePermissionMode(commandArr[1], commandArr[2]))
        elif(commandArr[0] == "deleteFile"):
            if (len(commandArr) != 2):
                print("Improper command")
                continue
            print(deleteFile(commandArr[1]))
        elif(commandArr[0] == "reset"):
            reset_database()
        elif (commandArr[0] == "logout"):
            print(logout())
        elif (commandArr[0] == "exit"):
            print(logout())
            print("Exiting...")
            break
        
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
    returnStr = ""
    # Change directory to home directory of user
    returnStr += changeDirectory(current_user.user_id) + "\n"
    # Check intergity of files 
    compFiles = checkIntergityOfFiles()
    if (compFiles != []):
        returnStr += "The following files have been changed by an unauthorized user since your last login: \n"
        for file in getPlainTextFilePaths(compFiles):
            returnStr += file + "\n"
    return returnStr + "Successfully login!"

def registerUser(username, password):
    global current_user
    if (db.check_user_exists(username) != None):
        return "User already exists"
    if (current_user != None):
        return "Already logged in, cannot register user!"
    userObj = db.register_user_in_database(username, password)
    # Create user home directory 
    outparams = file_manager.createDirectory(username)
    file_name_hash = file_manager.generateIntergityCodeForDirectory(outparams[0])
    db.create_home_dir(outparams[2], 
                       outparams[0], 
                       outparams[3], 
                       userObj, 
                       file_name_hash=file_name_hash)
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
    if not db.add_user_to_group(user, group):
        return "User already exists in group"
    return "User added to group"

def createFile(filename):
    if current_user == None:
        return "Must be logged in!"
    lookup_table = db.generate_rw_lookup_table(current_user)
    general_lookup_table = db.generate_general_lookup_table()
    enc_file_list = file_manager.getFileListInCurrentDir(general_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
        if dec_file == filename:
            return "File already exists"
    havePermission = False
    enc_parent_path = ""
    for enc_path in lookup_table:
            dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
            if dec_path == file_manager.current_path:
                havePermission = True
                enc_parent_path = enc_path
                break
    if (not havePermission):
        return "Do not have permission to do that command"
    outputparams = file_manager.createFile(filename)
    file_name_hash, file_hash = file_manager.generateIntegrityCode(outputparams[0], outputparams[0])
    db.create_file(outputparams[2], 
                   outputparams[0], 
                   outputparams[3], 
                   current_user, 
                   False,
                   enc_parent_path,
                   file_name_hash,
                   file_hash)
    return "File created!"

def deleteFile(filename):
    if current_user == None:
        return "Must be logged in!"
    general_lookup_table = db.generate_general_lookup_table()
    lookup_table = db.generate_rw_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(general_lookup_table)
    enc_file_name = ""
    fileExists = False
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
    fileObj = db.check_file_exists(enc_abs_path)
    if (fileObj.is_home_dir):
        return "Cannot delete home directory"
    file_manager.deleteFile(filename, general_lookup_table)
    db.delete_file(fileObj)
    return "File deleted"

def displayContents(filename):
    if current_user == None:
        return "Must be logged in!"
    enc_file_name = ""
    fileExists = False
    general_lookup_table = db.generate_general_lookup_table()
    lookup_table = db.generate_rw_lookup_table(current_user)
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
        return "Do not have permission to run this command"
    fileObj = db.check_file_exists(enc_abs_path)
    if (fileObj.is_dir):
        return "Is a directory, cannot display!"
    return file_manager.displayFileContents(filename, general_lookup_table)


def editFile(filename, contents):
    if current_user == None:
        return "Must be logged in!"
    general_lookup_table = db.generate_general_lookup_table()
    lookup_table = db.generate_rw_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(general_lookup_table)
    enc_file_name = ""
    fileExists = False
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
    fileObj = db.check_file_exists(enc_abs_path)
    if (fileObj.is_dir):
        return "Cannot edit a directory"
    file_manager.addFileContentsWrapper(filename, general_lookup_table, contents)
    file_name_hash, file_hash = file_manager.generateIntegrityCode(enc_file_name, enc_file_name)
    db.edit_file(fileObj, enc_abs_path, enc_file_name, file_name_hash, file_hash)
    return "File edited!"

def createDirectory(directoryname):
    if current_user == None:
        return "Must be logged in!"
    lookup_table = db.generate_rw_lookup_table(current_user)
    general_lookup_table = db.generate_general_lookup_table()
    enc_file_list = file_manager.getFileListInCurrentDir(general_lookup_table)
    for enc_file in enc_file_list:
        dec_file = file_manager.DecryptFileName(enc_file_list[enc_file][1], enc_file_list[enc_file][0])
        if dec_file == directoryname:
            return "Directory already exists"
    havePermission = False
    enc_parent_path = ""
    for enc_path in lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
        if dec_path == file_manager.current_path:
            havePermission = True
            enc_parent_path = enc_path
            break
    if (not havePermission):
        return "Do not have permission to do that command"
    outputparams = file_manager.createDirectory(directoryname)
    file_name_hash = file_manager.generateIntergityCodeForDirectory(outputparams[0])
    db.create_file(outputparams[2], 
                   outputparams[0], 
                   outputparams[3], 
                   current_user, 
                   True, 
                   enc_parent_path,
                   file_name_hash=file_name_hash)
    return "Directory created!"

def changeDirectory(directoryname):
    if current_user == None:
        return "Must be logged in!"
    if (directoryname == "../"):
        file_manager.changeDirectory(directoryname, {})
        return file_manager.relative_path
    fileExists = False
    access_lookup_table = db.generate_access_lookup_table(current_user)
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
    for enc_path in access_lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, access_lookup_table[enc_path][0])
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
    lookup_table = db.generate_general_lookup_table()
    permitted_lookup_table = db.generate_rw_lookup_table(current_user)
    if file_manager.current_path == file_manager.home_path:
        returnStr = ""
        for file in file_manager.listDir(lookup_table):
            returnStr += file + "\n"
        return returnStr[:-1]
    havePermission = False
    for enc_path in permitted_lookup_table:
        dec_path = file_manager.DecryptFileName(enc_path, permitted_lookup_table[enc_path][0])
        if dec_path == file_manager.current_path:
            enc_abs_path = enc_path
            havePermission = True
            break
    if (not havePermission):
        returnStr = ""
        for file in os.listdir():
            returnStr += file + "\n"
        return returnStr[:-1]
    returnStr = ""
    for file in file_manager.listDir(lookup_table):
        returnStr += file + "\n"
    return returnStr[:-1] 

def renameFile(old_file_name, new_file_name):
    if current_user == None:
        return "Must be logged in!"
    fileExists = False
    lookup_table = db.generate_rw_lookup_table(current_user)
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
    fileObj = db.check_file_exists(enc_old_abs_path)
    if (fileObj.is_home_dir):
        return "Cannot rename home directory of user"
    outparams = file_manager.renameFile_public(old_file_name, lookup_table, new_file_name)
    if (fileObj.is_dir):
        file_name_hash = file_manager.generateIntegrityCodeForDirectory(outparams[0])        
    else:
        file_name_hash, file_hash =  file_manager.generateIntegrityCode(outparams[0], outparams[0])
    db.rename_file(fileObj, outparams[2], outparams[0], file_name_hash)  
    return "File " + old_file_name + " renamed to " + new_file_name

def checkIntergityOfFiles():
    global current_user
    if current_user == None:
        return None
    lookup_table = db.generate_owned_lookup_table(current_user)
    comprisedFiles = []
    for enc_path in lookup_table:
        fileObj = db.check_file_exists(enc_path)
        dec_path = file_manager.DecryptFileName(enc_path, lookup_table[enc_path][0])
        if (fileObj.is_dir):
            if (not file_manager.verifyIntergityCodeForDirectory(dec_path)):
                comprisedFiles.append(fileObj)
        else:
            if (not file_manager.verifyIntegrityCode(dec_path, lookup_table[enc_path][1], fileObj.file_name_hash, fileObj.file_hash)):
                comprisedFiles.append(fileObj)
    return comprisedFiles


def changePermissionMode(filename, permission_mode):
    if current_user == None:
        return "Must be logged in to run command!"
    gen_lookup_table = db.generate_general_lookup_table()
    lookup_table = db.generate_owned_lookup_table(current_user)
    enc_file_list = file_manager.getFileListInCurrentDir(gen_lookup_table)
    enc_file_name = ""
    fileExists = True
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
    if (not db.set_permission_mode(fileObj, permission_mode)):
        return "Permission could not be changed"
    return "Permission changed"

def logout():
    global current_user
    current_user = None
    file_manager.resetToHomePath()
    returnStr = file_manager.relative_path
    return returnStr + "\nLogged out"

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
    dec_relative_path = os.path.join('/home', os.path.relpath(dec_path, file_manager.home_path))
    pathArray = dec_relative_path.split("/")
    fileLookup = db.generate_file_lookup_table()
    cleanedPathArr = []
    for pathEle in pathArray[2:]:
        dec_file = file_manager.DecryptFileName(pathEle, fileLookup[pathEle])
        cleanedPathArr.append(dec_file)
    cleaned_path = "/home"
    for cleanedPathEle in cleanedPathArr:
        cleaned_path += "/" + cleanedPathEle
    return cleaned_path

if __name__ == "__main__":
    main()