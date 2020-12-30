'''
● Looking for a server. You leave this state when you get an offer message.
● Connecting to a server. You leave this state when you successfully connect using TCP
● Game mode - collect characters and from the keyboard and send them over TCP. collect
data from the network and print it onscreen
'''
import os
import socket, threading
import struct
import datetime, time
import getch
import multiprocessing


# local host IP '127.0.0.1'
import sys
import time
#username = input("Enter port")
#host = '127.0.0.1'
host = ''

# Define the port on which you want to connect
port = 13117
port = 7002
tuching = True
def Main():
    continueask = True
    while continueask:
        Tcp_Port = udpState()
        if Tcp_Port != 0:
            tcpState(Tcp_Port)
        # if (input("continue? y/n") == 'n'):
        #     continueask = False
        # global tuching
        # tuching = True

    # print("finish")


def getTuch(soc):
    # global tuching
    # try:
    #     while tuching:
    then = datetime.datetime.now() + datetime.timedelta(seconds=10)
    try:
        while then > datetime.datetime.now():
            s ="c"
            print("go")
            tosend = getch.getch()
            #print(input("input"))
            # print("after inside")
            soc.send(s.encode())
    except:
        print("fail in getting tuch func")

class tuchthread(threading.Thread):
    def __init__(self,soc):
        threading.Thread.__init__(self)
        self.soc = soc
    def run(self):
        global tuching
        try:
            while tuching:
                s = "c"
                # print("go")
                tosend = getch.getch()
                # print(input("input"))
                # print("after inside")
                self.soc.send(s.encode())
        except:
            print("fail in getting tuch func")
        sys.exit()
    def raisexp(self):
        raise Exception("therad killed")

def tcpState(Tcp_Port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect to server on local computer
        print(host)
        print(Tcp_Port)
        s.connect((host, Tcp_Port))
        #m=s.recv(1028)
        # message you send to server
        team_name = "Korkifix"
        # message sent to server
        s.send(team_name.encode())
        # s.send(b'ascasd')
        # messaga received from server
        s.settimeout(40)
        try:

            starttype = s.recv(1024)
            starttype = starttype.decode()
            print(starttype)
            # game start
            # getTuch(s)
            #

            # print("before")
            # try:
            #     newthread = tuchthread(s)
            #     newthread.start()
            #     newthread.join(10)
            #     #time.sleep(5)
            #     #newthread.raisexp()
            #     global tuching
            #     tuching = False
            # except:
            #     print("cath exp")

            p = multiprocessing.Process(getTuch(s))
            p.daemon = True
            #p.join(10)
            print("asd")
            time.sleep(10)
            #p.terminate()

            # global tuching
            # tuching = False
            # print("after")
            # print("\n" * 100)
            # os.system('clear')
            print("timeFinish")
            try:
                winner = s.recv(1024)
                winner =winner.decode()
                print(winner)
                time.sleep(4)
            except:
                print("error happend while waiting for winner massege")
            # game end
        except:
            print("error happend while playing")
            # close the connection
        s.close()
    except:
        print("cant connect to tcp server")

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
            buffer,address = udp_socket.recvfrom(1024)
            unPackMsg = struct.unpack('I B H', buffer)
            if unPackMsg[0] == 0xfeedbeef and unPackMsg[1] == 0x2:
                x = False
            #test with our own server
            print (address[0])
            # if address[0] != '192.168.1.18':
            #     print("not good offer")
            #     x = True
            # else:
            #     print("goood offer")
            #     TCP_PORT = unPackMsg[2]
            #     print(TCP_PORT)
        TCP_PORT = unPackMsg[2]
        global host
        host = address[0]
        #host = '127.0.0.1'
        # host = '192.168.1.18'
        print(host)
        print(f"Received offer from {host}, attempting to connect...")
    except:
        print("can't connet to server udp")
    udp_socket.close()
    return TCP_PORT

if __name__ == '__main__':
    Main()


