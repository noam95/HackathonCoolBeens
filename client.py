'''
● Looking for a server. You leave this state when you get an offer message.
● Connecting to a server. You leave this state when you successfully connect using TCP
● Game mode - collect characters and from the keyboard and send them over TCP. collect
data from the network and print it onscreen
'''
import socket, threading
import struct
import datetime, time

import getch
import multiprocessing


# local host IP '127.0.0.1'
import sys
import time
host = ''

# Define the port on which you want to connect
port = 13117
tuching = True

def Main():
    continueask = True
    while continueask:
        Tcp_Port = udpState()
        if Tcp_Port != 0:
            tcpState(Tcp_Port)


def getTuch(soc):
    """
    This function hundle the keyboard pressing during the game
    :param soc: the socket
    :return:
    """
    then = datetime.datetime.now() + datetime.timedelta(seconds=10)
    try:
        while then > datetime.datetime.now():
            msg = "c"
            tosend = getch.getch()
            soc.send(msg.encode())
    except:
        print("fail in getting tuch func")



def tcpState(Tcp_Port):
    """
    This function runs the logic of the TCP state- which responsible to connect the clients
    :param Tcp_Port:  the port of the server
    :return:
    """
    try:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to server on local computer
        clientSocket.connect((host, Tcp_Port))

        # message you send to server
        team_name = "Korkifix"

        # message sent to server
        clientSocket.send(team_name.encode())

        clientSocket.settimeout(40)
        try:
            starttype = clientSocket.recv(1024)
            starttype = starttype.decode()
            print(starttype)
            # game start
            process = multiprocessing.Process(getTuch(clientSocket))

            print("Time finished, please wait for the result")
            try:
                #recieved winner message
                winner = clientSocket.recv(1024)
                winner = winner.decode()
                print(winner)
                time.sleep(4)
            except:
                #problem occur while waiting to game over message from server
                pass
            # game end
        except:
            #problem occur before the game started
            pass
        # close the  TCP connection
        clientSocket.close()
    except:
        pass

def udpState():
    """

    This function runs the UDP server which sends offers for 10 sec and connect all the clients
    that respond to those offers
    :return: the port of the udp server which is the same over tcp connection
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,socket.IPPROTO_UDP)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    TCP_PORT = 0
    udp_socket.bind(("", port))
    print("Client started, listening for offer requests...")
    flag = True
    #client recieving the udp offer and decode the format message
    try:
        while flag:
            buffer, address = udp_socket.recvfrom(1024)
            unPackMsg = struct.unpack('I B H', buffer)
            #checks if the UDP message is not in the required format
            if unPackMsg[0] == 0xfeedbeef and unPackMsg[1] == 0x2:
                flag = False

        TCP_PORT = unPackMsg[2]
        global host
        host = address[0]
        print(f"Received offer from {host}, attempting to connect...")
    except:
        #Theres been a problem to connect the UDP server
        pass

    #closing the UDP connection
    udp_socket.close()
    return TCP_PORT

if __name__ == '__main__':
    Main()


