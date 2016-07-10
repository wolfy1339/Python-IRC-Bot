from __future__ import print_function
import socket
from time import sleep
import config
# Config Settings
channel = config.channels
botnick = config.nick
realname = config.realname
ident = config.ident
password = config.password
username = config.username
nickserv = True


def connect():
    global irc
    print("Connecting to: " + config.server + "\n")
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # defines the socket
    irc.connect((config.server, config.port))  # connects to the server
    irc.setblocking(0)
    sendMsg(irc, "USER {0} {1} {1} :{2}\n".format(
        ident, botnick, realname))  # user authentication
    sendMsg(irc, "NICK {0}\n".format(botnick))  # sets nick
    if nickserv:
        sendMsg(irc, "ns identify {0} {1}\n".format(
          username, password))
    else:
        for i in channel:
            # join the channel(s)
            sendMsg(irc, "JOIN {0}\n".format(i))


def sendMsg(irc, msg):
    irc.send(msg.encode('UTF-8'))


def main():
    while True:
        # Receive data
        binary_data = irc.recv(2040)
        # Decode data from UTF-8
        data = binary_data.decode("UTF-8", "ignore")
        # Split data by spaces
        words = data.split()
        if words[1] == '396':
            # join channels only when idenified
            for i in channel:
                # join the channel(s)
                sendMsg(irc, "JOIN {0}\n".format(i))
        if words[0] == "PING":
            # Respond with PONG
            sendMsg(irc, "PONG {0}\n".format(words[1]).encode("UTF-8"))
        elif words[1] == "PRIVMSG":
            if " ".join(words[3:]) == ":Hello world!":
                channel = words[2]
                # Respond with a message saying "Hello!"
                sendMsg(irc, "PRIVMSG {0} :Hello!\n".format(channel))
            elif words[0][1:] in config.owner.hostmask and words[3] == "quit":
                reason = words[4:]
                if reason:
                    sendMsg(irc, "QUIT :{0}".format(reason))
                else:
                    sendMsg(irc, "QUIT :Quit requested by {0}".format(config.owner.nick))
            elif words[3] == "commands" or words[3] == "list":
                sendMsg(irc, "PRIVMSG {0} :NULL".format(channel))

        # Print the data
        try:
            print(data)
        except UnicodeEncodeError:
            pass

while True:  # puts it in an infinite loop
    try:
        connect()
        main()
        sleep(20)
    except KeyboardInterrupt:
        print("Keyboard inturrupt, bot shut down")
        break
    except Exception:
        print("A strange error occured, reconnecting in 10 seconds")
        sleep(10)
        pass
