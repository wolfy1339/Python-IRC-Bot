import socket
import sys
import json

config = json.loads("config.json")  # settings file
# Config Settings
server = config["network"]["server"]
port = config["network"]["port"]
channel = ",".join(config["channels"])
botnick = config["user"]["nick"]
realname = config["user"]["realname"]
ident = config["user"]["ident"]
password = config["user"]["password"]
username = config["user"]["username"]
x = (server, port)

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # defines the socket
print "connecting to:"+server
irc.connect(x)  # connects to the server
irc.send("USER {0} {1} blah :{2}\n".format(ident, botnick, realname).encode("UTF-8"))  # user authentication
irc.send("NICK {0}\n".format(botnick).encode("UTF-8"))  # sets nick
if username == "" || password == "":
    print "Username or Passwoord is empty! If that is not a mistake, please ignore this message"
else:
    irc.send("PRIVMSG nickserv :identify {0} {1}\r\n".format(username, password).encode("UTF-8"))  # auth
irc.send("JOIN {0}\n".format(channel).encode("UTF-8"))  # join the channel(s)

while 1:  # puts it in a loop
    text = irc.recv(2040)  # receive the text
    print text  # print text to console

    if text.find('PING') != -1:  # check if 'PING' is found
        irc.send('PONG ' + text.split()[1] + '\r\n')  # returns 'PONG' back to the server (prevents pinging out!)

    if text.find("*BWBellairs") != -1:
        irc.send("Yo... whoever you are")
