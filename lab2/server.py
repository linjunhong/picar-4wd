import bluetooth
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

def get_bluetooth_socket():
    hostMACAddress = "DC:A6:32:C7:72:C6" # The address of Raspberry PI Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
    port = 0
    backlog = 1
    size = 1024
    s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s.bind((hostMACAddress, port))
    print("listening on port ", port)

    return s


def start():
    wifi_socket = get_wifi_socket()
    bt_socket = get_bluetooth_socket()
    bt_socket.listen(1)

    try:
        wifi_client, wifi_client_info = wifi_socket.accept()
        print("[wifi] server received from:", wifi_client_info)

        bt_client, bt_clientInfo = s.accept()
        print("[bt] server received from:", bt_clientInfo)

        while 1:
            data = wifi_client.recv(1024)
            if (data != b""):
                print("Receive data from wifi:", data)
                wifi_client.sendall(data)

            data = bt_client.recv(1024)
            if data:
                print(data)
                client.send(data)

    except:
        print("Closing server")
        wifi_client.close()
        wifi_socket.close()
        bt_client.close()
        bt_socket.close()

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