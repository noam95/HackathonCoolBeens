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



"""
Game class is where the game logic happends
There are two T
"""
class game:


    #Attributes
    team1 = []
    team2 = []
    bol = True
    counter1 = 0
    counter2 = 0
    fastestPlayer = ["", 0]
    slowliestPlaer = ["", 0]
    totalpress= 0

    def assignToTeam(self, player):
        """
        This function divide the clients into two groups

        :param player: client thread
        :return: the name of the team the client belongs to
        """
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
        """
        Getting the message of groups
        :return: the message
        """
        msg ="group1\n"
        for i in self.team1:
            msg += i + "\n"
        msg += "group2\n"
        for i in self.team2:
            msg += i + "\n"
        return msg

    def updateScore(self, counter, grupName, name):
        """
        The function is updating the counters of each team and calculatin statistics of the game

        :param counter:  count the keyboard pressing
        :param grupName: name of the group the client belong to
        :param name: client name
        :return:
        """
        global gameClasslock1
        gameClasslock1.acquire(True)
        if grupName == "team1":
            self.counter1 += counter
        else:
            self.counter2 += counter
        self.totalpress += counter
        if counter > self.fastestPlayer[1]:
            self.fastestPlayer[1] = counter
            self.fastestPlayer[0] = name
        if counter < self.slowliestPlaer[1]:
            self.slowliestPlaer[1] = counter
            self.slowliestPlaer[0] = name
        #release the lock to keep this function sync
        gameClasslock1.release()

    def calculateScore(self):
        """
        The function calculate who wins the game

        :return: message with the game info. and winner
        """
        msg= "game has finished\ngroup1 get " + str(self.counter1) + " points.\n"
        msg += "group2 get " + str(self.counter2) + " points\n"
        msg += "The best player was " + self.fastestPlayer[0] + " he pressed " +str(self.fastestPlayer[1]) + " on keyboard\n"
        msg += "The worst player was " + self.slowliestPlaer[0] + " he pressed " + str(self.slowliestPlaer[1]) + " on keyboard\n"
        msg += "The average presses for all the players together was " + str(self.totalpress/(len(self.team2)+ len(self.team1))) + " press in 10 sec"
        msg += "\nAnd the winner is......."
        flag= False
        if self.counter1> self.counter2:
            flag = True
            msg += str(self.team1)
        if self.counter1< self.counter2:
            flag = True
            msg+= str(self.team2)
        if not flag:
            msg += "DRAW\n"
        msg += "Congratulations!!!!!!!!"
        return msg

    def reset(self):
        """
        The function reset all the variables that need to be restart before the next game

        :return:  None
        """
        self.team1 = []
        self.team2 = []
        self.bol = True
        self.counter1 = 0
        self.counter2 = 0
        self.fastestPlayer = ["", 0]
        self.slowliestPlaer = ["", 0]
        self.totalpress= 0

LOCALHOST = socket.gethostbyname(socket.gethostname())
# LOCALHOST = '172.18.0.108'
UDP_PORT = 13117
SERVER_TCP_PORT = 7000
server_to_connect ='172.1.0'
gameClasslock1 = threading.Lock()
getMessageLock1 = threading.Lock()
sendScoreLock1 = threading.Lock()
threads = []
game1 = game()

class bcolors:
    """
    The class is for colored messages on the terminal screen

    """
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
        udpthread.start()
        tcpthread = tcpConnection()
        tcpthread.start()
        tcpthread.join(10)
        udpthread.join(10)
        if(len(threads) != 0 ):
            getMessageLock1.release()#start game
            time.sleep(12)
            sendScoreLock1.release()#clculating score
            time.sleep(10)
            game1.reset()
        else:
            getMessageLock1.release()
            sendScoreLock1.release()

    #close all the threads
    #reset game

class udpThraed(threading.Thread):
    """
    The class hundle the UDP thread that we execute at the begining of the main function

    """
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        udpState()

class tcpConnection(threading.Thread):
    """
    The class hundle the TCP thread that we execute at the begining of the main function

    """
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        tcp_state()


class ClientThread(threading.Thread):
    """
    After responde to the UDP offer each client is connect over TCP protocol
    we generate thread for each client to run the program parallel
    """
    groupName = ""
    clientname = ""
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.clientAddress = clientAddress
        self.csocket = clientsocket

    def run(self):
        """
        The function define the running of threads in this class
        :return:
        """
        self.csocket.settimeout(40)#case no msg recived
        data = self.csocket.recv(2048)
        self.clientname = data.decode()
        self.groupName = game1.assignToTeam(self.clientname)
        global getMessageLock1
        while(getMessageLock1.locked()):
            time.sleep(0.01)
        val = self.startGameMassge()
        #lock for the send score function to keep it sync
        global sendScoreLock1
        while(sendScoreLock1.locked()):
            time.sleep(0.01)
        val = self.sendScore()
        if not val:
            return

    def startGameMassge(self):
        """
        The function sends the starting game message to all of the clients

        :return:
        """
        try:
            msg = '\033[95m' + 'Welcome to Keyboard Spamming Battle Royale.\n'+ bcolors.ENDC + bcolors.HEADER + bcolors.OKBLUE + bcolors.OKCYAN +'by KORKIFIX 077-202-4828 10 presents dicount for the winner!' + bcolors.ENDC+'\n'
            groupsMsg = '\033[94m' + game1.getGroupsMsg() + bcolors.ENDC
            startMsg =msg + groupsMsg+ bcolors.OKGREEN + '\nStart pressing keys on your keyboard as fast as you can!!\n'+ bcolors.ENDC
            self.csocket.send(startMsg.encode())
            counter_game = 0
            then = datetime.datetime.now() + datetime.timedelta(seconds=10)
            #the server recive keys pressing from client
            try:
                while then > datetime.datetime.now():
                    time.sleep(0.01)
                    self.csocket.settimeout(10)
                    if self.csocket.recv(1024):
                        counter_game += 1
            except:
                print("fail in getting typing from client")
                return False

            #after game update the main counter with the result of this client
            game1.updateScore(counter_game, self.groupName, self.clientname)
        except:
            print("client lost connection")
            return False

    def sendScore(self):
        try:
            msg = bcolors.WARNING + bcolors.BOLD + game1.calculateScore()+ bcolors.ENDC
            self.csocket.send(msg.encode())
        except:
            print("client lost connection")
            return False


def tcp_state():
    """
    The TCP state is after client respond to offer-
    then a TCP connection is open and all of the communication is over tcp socket
    :return:
    """
    try:
        # print(LOCALHOST)
        # print(SERVER_TCP_PORT)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((LOCALHOST, SERVER_TCP_PORT))
        server.settimeout(10)
        try:
            #connect client via tcp protocol and generate a client thread
            while True:
                server.listen(10)
                clientsock, clientAddress = server.accept()
                # print("some one tried to connect tcp")
                newthread = ClientThread(clientAddress, clientsock)
                newthread.start()
                threads.append(newthread)
        except:
            server.close()
            # print("tcp connection making time out")
    except:
        print("tcp connection refused/failed")


def udpState():
    """
    The UDP state is at the begining of the program
    The Upd server sends offers 1 each second in broadcast line
    after client respond he pass to the TCP state
    :return:
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    #pack the udp format with struct
    udp_offer_msg = struct.pack('I B H', 0xfeedbeef, 0x2, SERVER_TCP_PORT)

    print(f"Server started,listening on IP address {LOCALHOST}")
    then = datetime.datetime.now() + datetime.timedelta(seconds=10)
    while then > datetime.datetime.now():
        udp_socket.sendto(udp_offer_msg, (server_to_connect, UDP_PORT))
        # udp_socket.sendto(udp_offer_msg, ('<broadcast>', UDP_PORT))
        time.sleep(1)

    #closing the udp thread after 10 seconds of offering messages.
    udp_socket.close()

if __name__ == '__main__':
    Main()

