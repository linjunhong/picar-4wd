import bluetooth
import getopt
import json
import socket
import sys
import threading

from picar import *

# u - stop
# j - get data
# w - move forward
# s - move backward
# a - turn left
# d - turn right

def process_data(data, echo):
    for c in data:
        if (data == b'j'):
            json = get_data()
            echo(json)
        elif (data == b'u'):
            stop()
        else:
            move(data)

def listening_wifi():
    HOST = "192.168.1.110" # IP address of your Raspberry PI
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
                    print("[wifi] process data:", data)
                    process_data(data, client.sendall)

        except Exception as e: 
            print("[wifi] Encounter error:", e, "Closing socket")
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
    print("[bt] listening on port ", port,". Waiting for connection.")
    try:
        client, clientInfo = s.accept()
        while 1:   
            print("[bt] Waiting message from:", clientInfo)
            data = client.recv(size)
            if data:
                print("[bt] Received:", data)
                client.send("Currrent system time is: " + datetime.now().isoformat())
                print("[bt] Message sent.")

    except Exception as e: 
        print("[bt] Encounter error:", e, "Closing socket")
        client.close()
        s.close()

def start():
    wifi_thread = threading.Thread(target=listening_wifi, daemon=True)
    wifi_thread.start()
    bt_thread = threading.Thread(target=listening_bt, daemon=True)
    bt_thread.start()

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