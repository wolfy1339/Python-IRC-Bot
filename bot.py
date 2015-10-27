from __future__ import print_function
import socket
import sys
import json

with open("config.json") as config_file:
    config = json.load(config_file)  # settings file
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
print("connecting to: " + server + "\r\n")
irc.connect(x)  # connects to the server
irc.send("USER {0} {1} blah :{2}\r\n".format(
        ident, botnick, realname).encode("UTF-8"))  # user authentication
irc.send("NICK {0}\r\n".format(botnick).encode("UTF-8"))  # sets nick
if username == "" or password == "":
    print("Username or Passwoord is empty!")
    print("If that is not a mistake, please ignore this message")
else:
    irc.send("PRIVMSG NICKSERV :identify {0} {1}\r\n".format(
        username, password).encode("UTF-8"))  # auth
irc.send("JOIN {0}\r\n".format(channel).encode("UTF-8"))  # join the channel(s)

while True:  # puts it in an infinite loop
    binary_data = irc.recv(2048)
    # Decode data from UTF-8
    data = binary_data.decode("UTF-8", "ignore")
    # Split data by spaces
    words = data.split()
    if (words[1] == "PRIVMSG" and words[2].startswith("#") and
        " ".join(words[3:]) == ":Hello world!"):
        channel = words[2]
        # Respond with a message saying "Hello!"
        irc.send("PRIVMSG {0} :Hello!\r\n".format(channel).encode("UTF-8"))

    # Print the data
    try:
      print(data)
    except UnicodeEncodeError:
      pass
