import socket

HOST = "127.0.0.1"
PORT = 8000

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
        parseRecData(rec_data)
    return
    
def parseRecData(rec_data):
    rec_string = rec_data.decode()
    print(rec_string)
    return

def main():
    try:
        socket = setupServer()
        runServer(socket)
    except:
        print("Exception!")

def test_main():
    socket = setupServer()
    runServer(socket)

test_main()