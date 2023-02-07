import socket
import sqlite3
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
connection = sqlite3.connect("data.db")

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

def login(user, password):
    cursor = connection.cursor()
    userList = cursor.execute("SELECT USER_ID FROM USER_DATA")
    userExists = False
    for username in userList:
        if (username[0] == user):
            userExists = True
            break
    if (not userExists):
        return 1
    passwordCursor = cursor.execute("SELECT PASSWORD FROM USER_DATA WHERE USER_ID = \"{username}\"".format(username=user))
    for passW in passwordCursor:
        if (passW[0] == password):
            print("Successful login")
            return 0
    print("Incorrect password")
    cursor.close()
    return 2


def register(user, password):
    cursor = connection.cursor()
    userList = cursor.execute("SELECT USER_ID FROM USER_DATA")
    for username in userList:
        if (username[0] == user):
            print("User already exists")
            return 1
    print("Entering user into table")
    cursor.execute("INSERT INTO USER_DATA VALUES (\"{username}\", \"{password}\", NULL)".format(username=user,
                                                                                                password=password))
    print("Entered user into table")
    # os.mkdir("./root/" + user)
    # cursor.execute("INSERT INTO FILE_DATA")
    connection.commit()
    cursor.close()
    return 0

def parseRecData(rec_data, conn):
    rec_string = rec_data.decode()
    recStringArray = rec_string.split()
    if len(recStringArray) != 3:
        # send error response: improper command
        conn.sendall(3)
        return
    commandCode = 0
    try:
        commandCode = int(recStringArray[0])
    except ValueError:
        #send error response: improper command
        conn.sendall(3)
        return
    if (commandCode == 0):
        #login command
        commandResponse = login(recStringArray[0], recStringArray[1])
        conn.sendall(commandResponse)
    elif (commandCode == 1):
        #registration command
        commandResponse = register(recStringArray[0], recStringArray[1])
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
                register(registerArray[0], registerArray[1])
        elif (testString == "login"):
            loginParameters = input("Enter mock username and password\n")
            loginArray = loginParameters.split()
            if (len(loginArray) != 2):
                print("Invaild parameters")
            else:
                login(loginArray[0], loginArray[1])
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
    connection.close()