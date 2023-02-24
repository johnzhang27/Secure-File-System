import database_manager

db = database_manager.DatabaseManager()

def main():
    while True:
        command = input("Enter command: ")

def reset_database():
    db.drop_tables()
    db.create_tables()

def set_up_database():
    db.create_tables()

def registerUser(username, password):
    if (db.check_user_exists(username) != None):
        return "User already exists"
    db.register_user_in_database(username, password)
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

if __name__ == "__main__":
    main()