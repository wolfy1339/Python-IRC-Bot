from __future__ import print_function
import socket
import sys
import json
# Config Settings
channel = config.channels
botnick = config.nick
realname = config.realname
ident = config.ident
password = config.password
username = config.username
x = (config.server, config.port)

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # defines the socket
print("Connecting to: " + server + "\n")
irc.connect(x)  # connects to the server
irc.send("USER {0} {1} blah :{2}\n".format(
        ident, botnick, realname).encode("UTF-8"))  # user authentication
irc.send("NICK {0}\n".format(botnick).encode("UTF-8"))  # sets nick
if username == "" or password == "" and nickserv:
    print("Username or Password is empty!")
else if nickserv:
    irc.send("PRIVMSG NICKSERV :identify {0} {1}\n".format(
        username, password).encode("UTF-8"))  # auth
irc.send("JOIN {0}\n".format(channel).encode("UTF-8"))  # join the channel(s)

while True:  # puts it in an infinite loop
    # Receive data
    binary_data = irc.recv(4096)
    # Decode data from UTF-8
    data = binary_data.decode("UTF-8", "ignore")
    # Split data by spaces
    words = data.split()
    if words[0] == "PING":
        # Respond with PONG
        irc.send("PONG\n".encode("UTF-8"))
    elif words[1] == "PRIVMSG":
        if " ".join(words[3:]) == ":Hello world!":
            channel = words[2]
            # Respond with a message saying "Hello!"
            irc.send("PRIVMSG {0} :Hello!\n".format(channel).encode("UTF-8"))
        elif words[0][1:] in config.owner.hostmask and words[3] == "quit":
            reason = words[4:]
            if reason:
                irc.send("QUIT :{0}".format([" ".join(words[4:])]).encode("UTF-8"))
            else:
                irc.send("QUIT :Quit requested by {0}".format(config.owner.nick).encode("UTF-8"))
        elif words[3] == "commands" or words[3] == "list":
            irc.send("PRIVMSG {0} :NULL".format())
    # Print the data
    try:
        print(data)
    except UnicodeEncodeError:
        pass
