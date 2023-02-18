import socket
import sys
import os
import database_manager
import sqlalchemy

# https://docs.sqlalchemy.org/en/20/tutorial/engine.html
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html
# https://docs.sqlalchemy.org/en/20/core/engines.html

HOST = "127.0.0.1"
PORT = 8000
db = database_manager.DatabaseManager()
current_user = None
current_directory = ""

def setupServer():
    print("Setting up server")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return s

def runServer(socket):
    socket.listen()
    while True:
        conn, addr = socket.accept()
        handleRequest(conn, addr)

def handleRequest(conn, addr):
    with conn: 
        rec_data = b""
        while True:
            data = conn.recv(4096)
            if not data:
                break
            rec_data += data
        parseRecData(rec_data, conn)

def createGroup(groupname):
    if db.check_group_exists(groupname) != None:
        return "Group already exists"
    db.create_group_in_database(groupname)
    return "Group successfuly registered"

def login(username, password):
    global current_user
    user_obj = db.check_user_exists(username)
    if user_obj == None:
        return "User does not exist"
    if not db.login_in_user(username, password):
        return "Password does not match"
    print(user_obj)
    current_user = user_obj
    return "Successfully login!"

def registerUser(username, password):
    if (db.check_user_exists(username) != None):
        return "User already exists"
    db.register_user_in_database(username, password)

def addUserToGroup(username, groupname):
    user = db.check_user_exists(username)
    group = db.check_group_exists(groupname)
    if user == None:
        return "Specified user does not exist"
    if group == None:
        return "Specified group does not exist"
    db.add_user_to_group(user, group)

def createFile(path, filename):
    if (db.check_file_exists(current_directory + path) != None):
        return "File already exists, cannot create"
    current_dir = db.check_file_exists(current_directory)
    if (not db.check_file_permissions(current_dir, current_user)):
        return "Do not have permission to create files in this directory"
    db.create_dir(abspath, filename, current_user)
    return "File created!"

def parseRecData(rec_data, conn):
    rec_string = rec_data.decode()
    recStringArray = rec_string.split()
    if len(recStringArray) != 3:
        # send error response: improper command
        conn.sendall("Improper command")
        return
    commandCode = 0
    try:
        commandCode = int(recStringArray[0])
    except ValueError:
        #send error response: improper command
        conn.sendall("Improper command")
        return
    if (commandCode == 0):
        #login command
        commandResponse = login(recStringArray[0], recStringArray[1])
        conn.sendall(commandResponse)
    elif (commandCode == 1):
        #registration command
        commandResponse = registerUser(recStringArray[0], recStringArray[1])
        conn.sendall(commandResponse)
    return

def debugMode():
    print("In debug mode.")
    while True:
        testString = input("Enter test command or EXIT for exit\n")
        if (testString == "register"):
            registerParameters = input("Enter mock username and password\n")
            registerArray = registerParameters.split()
            if (len(registerArray) != 2):
                print("Invaild parameters")
            else:
                print(registerUser(registerArray[0], registerArray[1]))
        elif (testString == "login"):
            loginParameters = input("Enter mock username and password\n")
            loginArray = loginParameters.split()
            if (len(loginArray) != 2):
                print("Invaild parameters")
            else:
                print(login(loginArray[0], loginArray[1]))
        elif (testString == "createGroup"):
            groupParams = input("Enter group name: \n")
            groupArr = groupParams.split()
            if (len(groupArr) != 1):
                print("Invaild parameters")
            else:
                print(createGroup(groupArr[0]))
        elif (testString == "addToGroup"):
            addParams = input("Enter user and group: \n")
            addArr = addParams.split()
            if (len(addArr) != 2):
                print("Invaild parameters")
            else:
                print(addUserToGroup(addArr[0], addArr[1]))
        elif (testString == "createFile"):
            createParams = input("Enter path and name: \n")
            createArr = createParams.split()
            if (len(createArr) != 2):
                print("Invaild parameters")
            else:
                print(createFile(createArr[0], createArr[1]))
        elif (testString == "EXIT"):
            db.close_session()
            break
        else:
            continue
    return

def main():
    if (len(sys.argv) > 2):
        print("Invaild number of arguments")
        return
    elif (len(sys.argv) == 2 and sys.argv[1] == "-debug"):
        debugMode()
        return
    elif (len(sys.argv) ==2 and sys.argv[1] != "-debug"):
        print("Invaild argument")
        return
    else:
        print("Server mode")
        try:
            socket = setupServer()
            runServer(socket)
        except:
            print("Exception!")
   
if __name__ == "__main__":
    main()