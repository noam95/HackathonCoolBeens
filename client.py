'''
● Looking for a server. You leave this state when you get an offer message.
● Connecting to a server. You leave this state when you successfully connect using TCP
● Game mode - collect characters and from the keyboard and send them over TCP. collect
data from the network and print it onscreen
'''
import msvcrt
import socket
import struct
import datetime, time


# local host IP '127.0.0.1'
import time

host = '127.0.0.1'

# Define the port on which you want to connect
port = 13117
def tcpState(Tcp_Port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to server on local computer
    s.connect((host, Tcp_Port))
    #m=s.recv(1028)
    # message you send to server
    message = "shaurya says geeksforgeeks"
    team_name = "Korkifix"
    # message sent to server
    s.send(team_name.encode())
    # s.send(b'ascasd')
    # messaga received from server
    s.settimeout(40)
    try:
        welcomeMSG = s.recv(1024)
        welcomeMSG = welcomeMSG.decode()
        print(welcomeMSG)
        s.send(b'ack')
        groups = s.recv(1024)
        groups = groups.decode()
        print(groups)
        s.send(b'ack')
        starttype = s.recv(1024)
        starttype = starttype.decode()
        print(starttype)
        # game start
        then = datetime.datetime.now() + datetime.timedelta(seconds=10)
        g = msvcrt.getch()
        while then > datetime.datetime.now():
            # time.sleep(1)
            print("s")
            s.send(g)  # check if this line sends key pressing
        print("timeFinish")
        try:
            winner = s.recv(1024)
            winner =winner.decode()
            print(winner)
        except:
            print("error happend while waiting for winner massege")
        # game end
    except:
        print("error happend while playing")
        # close the connection
    s.close()

def udpState():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    TCP_PORT = 0
    udp_socket.bind(("",port))
    print("Client started, listening for offer requests...")
    x = True
    #udp_socket.settimeout(20)
    try:
        while x:
            buffer = udp_socket.recv(1024)
            unPackMsg = struct.unpack('Ibh', buffer)
            if unPackMsg[0] == 0xfeedbeef and unPackMsg[1] == 0x2:
                x = False
        TCP_PORT = unPackMsg[2]
        iphost= host
        print(f"Received offer from {iphost}, attempting to connect...")
    except:
        print("can't connet to server")
    udp_socket.close()
    return TCP_PORT
while True:
    Tcp_Port = udpState()
    if Tcp_Port != 0:
        tcpState(Tcp_Port)