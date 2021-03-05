import getopt
import socket
import sys

def get_wifi_socket():
    HOST = "192.168.1.110" # IP address of your Raspberry PI
    PORT = 65432            # Port to listen on (non-privileged ports are > 1023)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()

    return s

def start():
    wifi_socket = get_wifi_socket()

    try:
        while 1:
            print("new cycle")
            wifi_client, wifi_client_info = wifi_socket.accept()
            print("server received from:", wifi_client_info)
            data = wifi_client.recv(1024)
            if (data != b""):
                print(data)
                wifi_client.sendall(data)
                print("end")

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