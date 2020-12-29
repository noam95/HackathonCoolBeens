'''
Waiting for clients - sending out offer messages and responding to request messages
and new TCP connections. You leave this state after 10 seconds.
● Game mode - collect characters from the network and calculate the score. You leave this
state after 10 seconds.
'''

import socket, threading
import struct
import time
from pip._vendor.distlib.compat import raw_input
from concurrent.futures import ThreadPoolExecutor
import datetime, time

class game:
    team1 = []
    team2 = []
    bol = True
    counter1 = 0
    counter2 = 0


    def assignToTeam(self, player):
        gameClasslock.acquire(True)
        if self.bol:
            self.team1.append(player)
            self.bol = False
            gameClasslock.release()
            return "team1"
        else:
            self.team2.append(player)
            self.bol = True
            gameClasslock.release()
            return "team2"

    def getGroupsMsg(self):
        msg ="group1\n"
        for i in self.team1:
            msg += i + "\n"
        msg += "group2\n"
        for i in self.team2:
            msg += i + "\n"
        return msg

    def updateScore(self, counter, grupName):
        gameClasslock.acquire(True)
        if (grupName == "team1"):
            self.counter1 += counter
        else:
            self.counter2 += counter
        gameClasslock.release()

    def calculateScore(self):
        msg= "game over\ngroup1 get"+ str(self.counter1) +"points.\n"
        msg += "group2 get" + str(self.counter2) + "points\n"
        msg += "and the winer is......."
        if self.counter1> self.counter2:
            msg += str(self.team1)
        if self.counter1< self.counter2:
            msg+= str(self.team2)
        else:
            msg+= "tekooooo\n"
        msg += "Congratulations!!!!!!!!"
        return msg
    def reset(self):
        self.team1 = []
        self.team2 = []
        self.bol = True
        self.counter1 = 0
        self.counter2 = 0


LOCALHOST = "127.0.0.1"
UDP_PORT = 13117
SERVER_TCP_PORT = 7000
gameClasslock = threading.Lock()
getMessageLock = threading.Lock()
sendScoreLock = threading.Lock()
threads = []

game1 = game()


def Main():
    while True:
        getMessageLock.acquire()
        sendScoreLock.acquire()
        udpthread = udpThraed()
        print("udpThred start")
        udpthread.start()
        tcpthread = tcpConnection()
        print("tcp thread start")
        tcpthread.start()
        tcpthread.join(10)
        udpthread.join(10)
        print("udp/tcp thread finished")
        if(len(threads) != 0 ):
            # groupsMsg = game1.getGroupsMsg()
            getMessageLock.release()#start game
            time.sleep(12)
            print("game Finished")
            sendScoreLock.release()#clculating score
            time.sleep(10)
            game1.reset()
        else:
            getMessageLock.release()
            sendScoreLock.release()

    #close all the threads
    #reset game

class udpThraed(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        udpState()

class tcpConnection(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        tcp_state()

class ClientThread(threading.Thread):
    groupName = ""
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.clientAddress = clientAddress
        self.csocket = clientsocket

    def run(self):
        self.csocket.settimeout(40)#case no msg recived
        data = self.csocket.recv(2048)
        clientname = data.decode()
        self.groupName = game1.assignToTeam(clientname)
        while(getMessageLock.locked()):
            pass
        val = self.startGameMassge()
        if not val:
            return
        while(sendScoreLock.locked()):
            pass
        val = self.sendScore()
        if not val:
            return

    def startGameMassge(self):
        try:
            msg = 'Welcome to Keyboard Spamming Battle Royale.'
            self.csocket.send(msg.encode())
            self.csocket.recv(1024)
            groupsMsg = game1.getGroupsMsg()
            self.csocket.send(groupsMsg.encode())
            self.csocket.recv(1024)
            startMsg = 'Start pressing keys on your keyboard as fast as you can!!'
            self.csocket.send(startMsg.encode())

            counter_game = 0
            then = datetime.datetime.now() + datetime.timedelta(seconds=10)
            try:
                while then > datetime.datetime.now():

                    self.csocket.settimeout(10)
                    if self.csocket.recv(1024):
                        counter_game += 1
            except:
                print("fail in getting typing from client")
                return False

            game1.updateScore(counter_game, self.groupName)
            print(counter_game)
        except:
            print("client lost connection")
            return False
    def sendScore(self):
        try:
            msg = game1.calculateScore()
            self.csocket.send(msg.encode())
        except:
            print("client connection lost")
            return False




        #game1.assignToTeam(groupName)
        # msg = ''
        #     if msg == 'bye':
        #         break
        #     print("from client", msg)
        #     self.csocket.send(bytes(msg, 'UTF-8'))
        # print("Client at ", self.clientAddress, " disconnected...")


def tcp_state():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((LOCALHOST, SERVER_TCP_PORT))
    while True:
        server.listen(10)
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()
        threads.append(newthread)

def udpState():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    #pack the udp format with struct
    udp_offer_msg = struct.pack('Ibh', 0xfeedbeef, 0x2, SERVER_TCP_PORT)

    print("Server started,listening on IP address 172.1.0.1")
    then = datetime.datetime.now() + datetime.timedelta(seconds=10)
    while then > datetime.datetime.now():
        udp_socket.sendto(udp_offer_msg, ('<broadcast>', UDP_PORT))
        time.sleep(1)

    #closing the udp thread after 10 seconds of offering messages.
    udp_socket.close()

if __name__ == '__main__':
    Main()

