import database_manager
import file_manager

# CLI for the server admin for managing database, users, and groups

db = database_manager.DatabaseManager("data.db")
file_manager = file_manager.FileManager()

def reset_database():
    db.drop_tables()
    db.create_tables()

def set_up_database():
    db.create_tables()

def registerUser(username, password):
    if (db.check_user_exists(username) != None):
        return "User already exists"
    userObj = db.register_user_in_database(username, password)
    outparams = file_manager.createDirectory(username)
    file_name_hash = file_manager.generateIntergityCodeForDirectory(outparams[0])
    db.create_home_dir(outparams[2], 
                       outparams[0], 
                       outparams[3], 
                       userObj, 
                       file_name_hash=file_name_hash)
    return "User registered!"

def removeUser(username):
    userObj = db.check_user_exists(username)
    if (userObj == None):
        return "User does not exist!"
    homeDir = db.get_user_home_directory(userObj)
    if (homeDir == None):
        return "User does not have a home directory"
    file_manager.deleteFile(username, db.generate_general_lookup_table())
    db.remove_user_in_database(userObj)
    return "User and files removed!"

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

def removeUserFromGroup(username, groupname):
    user = db.check_user_exists(username)
    group = db.check_group_exists(groupname)
    if user == None:
        return "Specified user does not exist"
    if group == None:
        return "Specified group does not exist"
    if not db.remove_user_from_group(user, group):
        return "User not in group"
    return "User removed"

def main():
    while True:
        command = input("Enter command: ")
        commandArr = command.split()
        if (commandArr[0] == "register"):
            if (len(commandArr) != 3):
                print("Improper command")
                continue
            print(registerUser(commandArr[1], commandArr[2]))
        elif (commandArr[0] == "removeUser"):
            if (len(commandArr) != 2):
                print("Improper command")
                continue
            print(removeUser(commandArr[1]))
        elif (commandArr[0] == "createGroup"):
            if (len(commandArr) != 2):
                print("Improper command")
                continue
            print(createGroup(commandArr[1]))
        elif (commandArr[0] == "addUserToGroup"):
            if (len(commandArr) != 3):
                print("Improper command")
                continue
            print(addUserToGroup(commandArr[1], commandArr[2]))
        elif (commandArr[0] == "removeUserFromGroup"):
            if (len(commandArr) != 3):
                print("Improper command")
                continue
            print(removeUserFromGroup(commandArr[1], commandArr[2]))
        elif(commandArr[0] == "reset"):
            print("Resetting database...")
            reset_database()
        elif(commandArr[0] == "set_up"):
            print("Setting up database...")
            set_up_database()
        elif (commandArr[0] == "exit"):
            print("Exiting...")
            break
        else:
            print("Improper command")

if __name__ == "__main__":
    main()