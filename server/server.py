import socket
import sys
import os
import classes
import sqlalchemy

# https://docs.sqlalchemy.org/en/20/tutorial/engine.html
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html
# https://docs.sqlalchemy.org/en/20/core/engines.html

HOST = "127.0.0.1"
PORT = 8000
engine_connection = classes.engine.connect()

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
    session = sqlalchemy.orm.Session(classes.engine)
    groups = sqlalchemy.select(classes.Group)
    for group in session.scalars(groups):
        if group.group_id == groupname:
            session.close()
            return str(1) + " Group already exists"
    newGroup = classes.Group(group_id=groupname)
    session.add(newGroup)
    session.commit()
    session.close()
    return str(0) + " Group successfuly registered"

def login(username, password):
    session = sqlalchemy.orm.Session(classes.engine)
    users = sqlalchemy.select(classes.User)
    userExists = False
    for user in session.scalars(users):
        if user.user_id == username:
            userExists = True
            break
    if not userExists:
        session.close()
        return str(1) + " User does not exist"
    passwordSt = sqlalchemy.select(classes.User.password).where(classes.User.user_id == username)
    passwordRec = session.execute(passwordSt).first()[0]
    if (passwordRec != password):
        session.close()
        return str(1) + " Password does not match"
    session.close()
    return 2 + " Successfully login!"

def registerUser(username, password):
    session = sqlalchemy.orm.Session(classes.engine)
    created_user = classes.User(
        user_id=username,
        password=password)

    users = sqlalchemy.select(classes.User)
    for user in session.scalars(users):
        if user.user_id == username:
            session.close()
            return str(1) + " User already exists"
    session.add(created_user)
    session.commit()
    session.close()
    return str(0) + " User successfuly registered"

def parseRecData(rec_data, conn):
    rec_string = rec_data.decode()
    recStringArray = rec_string.split()
    if len(recStringArray) != 3:
        # send error response: improper command
        conn.sendall(str(3) + " Improper command")
        return
    commandCode = 0
    try:
        commandCode = int(recStringArray[0])
    except ValueError:
        #send error response: improper command
        conn.sendall(str(3) + " Improper command")
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
        elif (testString == "EXIT"):
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
    engine_connection.close()