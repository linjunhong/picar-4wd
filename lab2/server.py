import bluetooth
import getopt
import socket
import sys
import threading

def listening_wifi():
    HOST = "192.168.3.49" # IP address of your Raspberry PI
    PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        try:
            client, clientInfo = s.accept()
            while 1:
                print("[wifi] server recv from: ", clientInfo)
                data = client.recv(1024)      # receive 1024 Bytes of message in binary format
                if data != b"":
                    print("[wifi] data:", data)     
                    client.sendall(data) # Echo back to client
        except: 
            print("[wifi] Closing socket")
            client.close()
            s.close()    

def listening_bt():
    hostMACAddress = "DC:A6:32:C7:72:C6" # The address of Raspberry PI Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
    port = 0
    backlog = 1
    size = 1024
    s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    s.bind((hostMACAddress, port))
    s.listen(backlog)
    print("[bt] listening on port ", port)
    try:
        client, clientInfo = s.accept()
        while 1:   
            print("[bt] server recv from: ", clientInfo)
            data = client.recv(size)
            if data:
                print("[bt] data:", data)
                client.send(data) # Echo back to client
    except: 
        print("Closing socket")
        client.close()
        s.close()



def start():
    wifi_thread = threading.Thread(target=listening_wifi, daemon=True)
    wifi_thread.start()
    bt_thread = threading.Thread(target=listening_bt, daemon=True)
    bt_thread()

    wifi_thread.join()
    bt_thread.join()

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