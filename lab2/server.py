import getopt
import socket
import sys

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    try:
        while 1:
            client, clientInfo = s.accept()
            print("server recv from: ", clientInfo)
            data = client.recv(1024)      # receive 1024 Bytes of message in binary format
            if data != b"":
                print(data)     
                client.sendall(data) # Echo back to client
    except: 
        print("Closing socket")
        client.close()
        s.close()    

def start():
    wifi_socket = get_wifi_socket()

    try:
        while 1:
            wifi_client, wifi_client_info = wifi_socket.accept()
            print("server received from:", wifi_client_info)
            data = wifi_client.recv(1024)
            if (data != b""):
                print(data)
                wifi_client.sendall(data)

    except:
        print("Closing server")
        wifi_client.close()
        wifi_socket.close()

    return

def main(argv):
    try:
      opts, args = getopt.getopt(argv,"f:p:q:r:")
    except getopt.GetoptError:
      print("move.py -f <function> -p <paramter>")
      sys.exit(2)

    command = None
    for opt, arg in opts:
        if opt == "-f":
            command = arg
        elif opt == "-p":
            parameter1 = arg

    if (command == "start"):
        start()
    
    return

if __name__ == '__main__':
    main(sys.argv[1:])