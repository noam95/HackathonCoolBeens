'''
Waiting for clients - sending out offer messages and responding to request messages
and new TCP connections. You leave this state after 10 seconds.
● Game mode - collect characters from the network and calculate the score. You leave this
state after 10 seconds.
'''


import socket, threading
import struct
import time
import datetime, time

class game:
    team1 = []
    team2 = []
    bol = True
    counter1 = 0
    counter2 = 0


    def assignToTeam(self, player):
        global gameClasslock1
        gameClasslock1.acquire(True)
        if self.bol:
            self.team1.append(player)
            self.bol = False
            gameClasslock1.release()
            return "team1"
        else:
            self.team2.append(player)
            self.bol = True
            gameClasslock1.release()
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
        global gameClasslock1
        gameClasslock1.acquire(True)
        if (grupName == "team1"):
            self.counter1 += counter
        else:
            self.counter2 += counter
        gameClasslock1.release()

    def calculateScore(self):
        msg= "game has finished\ngroup1 get "+ str(self.counter1) +" points.\n"
        msg += "group2 get " + str(self.counter2) + " points\n"
        msg += "and the winer is......."
        flag= False
        if self.counter1> self.counter2:
            flag = True
            msg += str(self.team1)
        if self.counter1< self.counter2:
            flag = True
            msg+= str(self.team2)
        if not flag:
            msg+= "tekooooo\n"
        msg += "Congratulations!!!!!!!!"
        return msg
    def reset(self):
        self.team1 = []
        self.team2 = []
        self.bol = True
        self.counter1 = 0
        self.counter2 = 0

LOCALHOST = socket.gethostbyname(socket.gethostname())
# LOCALHOST = '172.18.0.108'
print(LOCALHOST)
UDP_PORT = 13117
#UDP_PORT = 7001
SERVER_TCP_PORT = 7000
gameClasslock1 = threading.Lock()
getMessageLock1 = threading.Lock()
sendScoreLock1 = threading.Lock()
threads = []
game1 = game()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def Main():
    while True:
        global getMessageLock1
        global sendScoreLock1

        getMessageLock1.acquire()
        sendScoreLock1.acquire()
        udpthread = udpThraed()
        print('\033[93m'+"udpThred start"+ bcolors.ENDC)
        udpthread.start()
        tcpthread = tcpConnection()
        print("tcp thread start")
        tcpthread.start()
        tcpthread.join(10)
        udpthread.join(10)
        print("udp/tcp thread finished")
        if(len(threads) != 0 ):
            # groupsMsg = game1.getGroupsMsg()
            getMessageLock1.release()#start game
            time.sleep(12)
            print("game Finished")
            sendScoreLock1.release()#clculating score
            time.sleep(10)
            game1.reset()
        else:
            getMessageLock1.release()
            sendScoreLock1.release()

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
        global getMessageLock1
        while(getMessageLock1.locked()):
            pass
        val = self.startGameMassge()
        # if not val:#player is not playing
        #
        #     return
        global sendScoreLock1
        while(sendScoreLock1.locked()):
            pass
        val = self.sendScore()
        if not val:
            return

    def startGameMassge(self):
        try:
            msg = '\033[95m' + 'Welcome to Keyboard Spamming Battle Royale.\n'+ bcolors.ENDC + bcolors.HEADER + bcolors.OKBLUE + bcolors.OKCYAN +'by KORKIFIX 077-202-4828 10 presents dicount for the winner!' + bcolors.ENDC+'\n'
            # self.csocket.send(msg.encode())
            #self.csocket.recv(1024)
            groupsMsg = '\033[94m' + game1.getGroupsMsg() + bcolors.ENDC
            # self.csocket.send(groupsMsg.encode())
            # self.csocket.recv(1024)
            startMsg =msg + groupsMsg+ bcolors.OKGREEN + '\nStart pressing keys on your keyboard as fast as you can!!\n'+ bcolors.ENDC
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
            msg = bcolors.WARNING + bcolors.BOLD + game1.calculateScore()+ bcolors.ENDC
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
    try:
        print(LOCALHOST)
        print(SERVER_TCP_PORT)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((LOCALHOST, SERVER_TCP_PORT))
        server.settimeout(10)
        try:
            while True:
                server.listen(10)
                clientsock, clientAddress = server.accept()
                print("some one tried to connect tcp")
                newthread = ClientThread(clientAddress, clientsock)
                newthread.start()
                threads.append(newthread)
        except:
            server.close()
            print("tcp connection making time out")
    except:
        print("tcp connection refused/faileddddd")

def udpState():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    #pack the udp format with struct
    udp_offer_msg = struct.pack('I B H', 0xfeedbeef, 0x2, SERVER_TCP_PORT)

    print(f"Server started,listening on IP address {LOCALHOST}")
    then = datetime.datetime.now() + datetime.timedelta(seconds=10)
    while then > datetime.datetime.now():
        udp_socket.sendto(udp_offer_msg, ('172.1.0', UDP_PORT))
        time.sleep(1)

    #closing the udp thread after 10 seconds of offering messages.
    udp_socket.close()

if __name__ == '__main__':
    Main()

