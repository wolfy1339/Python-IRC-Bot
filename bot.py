from __future__ import print_function
import socket
import select
import traceback
from time import sleep
import os
import sys
import atexit
import imp
import hashlib
import random

if not os.path.isfile("config.json"):
    import shutil
    shutil.copyfile("configtemplate.json", "config.json")
    print("configtemplate.json copied to config.json")

from config import *
if not configured:
    print("You have not configured the bot, open up config.json to edit settings")
    quit()

from common import *
mods = {}
for i in os.listdir("mods"):
    if os.path.isfile(os.path.join("mods", i)) and i[-3:] == ".py" and i[:-3] not in disabledPlugins:
        try:
            mods[i[:-3]] = imp.load_source(i[:-3], os.path.join("mods", i))
        except Exception:
            pass

def SocketSend(socket, message):
    socket.send(message.encode('utf-8'))

def Print(message):
    if encoding != "utf-8":
        message = message.encode(encoding, errors="replace").decode(encoding)
    # Python throws an error when it sees the | character sent
    elif message.find(u"\2502") !=-1:
        message = message.lstrip(u"\u2502")
    print(message)

def Connect():
    global irc
    Print("Connecting to {0}...".format(server))
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc.connect((server,port))
    irc.setblocking(0)
    SocketSend(irc, "USER {0} {1} {2} :{3}\n".format(botIdent, botNick, botNick, botRealname))
    SocketSend(irc, "NICK {0}\n".format(botNick))
    if NickServ:
        SocketSend(irc, "ns identify {0} {1}\n".format(botAccount, botPassword))
    else:
        SocketSend(irc, "JOIN {0}\n".format(channels))

def PrintError(channel = None):
    Print("=======ERROR=======\n{0}========END========\n".format(traceback.format_exc()))
    if channel:
        if channel[0] != "#":
            channel = errorchannel
        SocketSend(irc, "PRIVMSG {0} :Error printed to console\n".format(channel))
        if errorCode:
            try:
                exec(errorCode)
            except Exception:
                SocketSend(irc, "PRIVMSG {0} :We heard you like errors, so we put an error in your error handler so you can error while you catch errors\n".format(channel))
    
def Interrupt():
    SocketSend(irc, "QUIT :Keyboard Interrupt\n")
    irc.close()
    quit()

def main():
    socketQueue = b""
    while True:
        try:
            lines = b""
            ready = select.select([irc], [], [], 1.0)
            if ready[0]:
                lines = irc.recv(2040)
        except Exception: #socket.error, e:   or   socket.timeout, e:
            PrintError()
            return
        else:
            lines = socketQueue + lines # add on any queue from the last recv
            linesSplit = lines.splitlines()
            socketQueue = b""
            if lines and lines[-1] != ord("\n"):
                socketQueue = linesSplit.pop()
            for line in linesSplit:
                try:
                    line = line.decode("utf-8", errors="replace")
                    Print("<-- " + line + "\n")
                    text = line.split()

                    if len(text) > 0:
                        #Reply to server pings
                        if text[0] == "PING":
                            SocketSend(irc, "PONG {0}\n".format(text[1]))
                        elif text[0] == "ERROR":
                            irc.close()
                            return #try to reconnect

                    if len(text) > 1:
                        # Only join channel once identified
                        if text[1] == "396":
                            SocketSend(irc, "JOIN {0}\n".format(channels))
                        # Nickname already in use
                        elif text[1] == "433":
                            SocketSend(irc, "NICK {0}-\n".format(text[3]))
                            if NickServ:
                                SocketSend(irc, "ns identify {0} {1}\n".format(botAccount, botPassword))
                                SocketSend(irc, "ns ghost {0}\n".format(botNick))
                                SocketSend(irc, "NICK {0}\n".format(botNick))
                        # Nickname temporarily unavailable
                        elif text[1] == "437":
                            SocketSend(irc, "NICK {0}-\n".format(text[3]))
                            if NickServ:
                                SocketSend(irc, "ns identify {0} {1}\n".format(botAccount, botPassword))
                                SocketSend(irc, "ns release {0}\n".format(botNick))
                                SocketSend(irc, "NICK {0}\n".format(botNick))

                    if len(text) > 2:
                        # Get channel to reply to
                        if text[1] == "PRIVMSG":
                            reply = text[2]
                            if reply == botNick:
                                reply = text[0].split("!")[0].lstrip(":")
                        elif text[1] == "NICK" and text[0].split("!")[0][1:] == botNick:
                            SocketSend(irc, "NICK {0}\n".format(botNick))

                    if len(text) >= 4:
                        #Parse line in stocks.py
                        if len(text):
                            Parse(text)

                    #allow modules to do their own text parsing if needed, outside of raw commands
                    for mod in mods:
                         if hasattr(mods[mod], "Parse"):
                            mods[mod].Parse(line, text)
                except SystemExit:
                    SocketSend(irc, "QUIT :{0}\n".format(quitMessage))
                    irc.close()
                    quit()
                except Exception:
                    PrintError(errorchannel or channels[0])
        try:
            #allow modules to have a "tick" function constantly run, for any updates they need
            for mod in mods:
                if hasattr(mods[mod], "AlwaysRun"):
                    mods[mod].AlwaysRun(channels[0])
            #TODO: maybe proper rate limiting, but this works for now
            temp = False
            if len(messageQueue) > 7:
                temp = True
            for i in messageQueue:
                Print("--> {0}".format(i))
                SocketSend(irc, i)
                if temp:
                    sleep(1)
            messageQueue[:] = []
        except Exception:
            PrintError(errorchannel or channels[0])

def Parse(text):
    if text[1] == "PRIVMSG":
        channel = text[2]
        username = text[0].split("!")[0].lstrip(":")
        hostmask = text[0].split("!")[1]
        command = text[3].lower().lstrip(":")
        if channel == botNick:
            channel = username

        #some special owner commands that aren't in modules
        if CheckOwner(text[0]):
            if command == "{0}reload".format(commandChar):
                if len(text) <= 4:
                    SendNotice(username, "No module given")
                    return
                mod = text[4]
                if not os.path.isfile(os.path.join("mods", mod + ".py")):
                    return
                commands[mod] = []
            elif command == "{0}eval".format(commandChar):
                try:
                    command = " ".join(text[4:]).replace("\\n", "\n").replace("\\t", "\t")
                    ret = str(eval(command))
                except Exception as e:
                    ret = str(type(e)) + ":" + str(e)
                SendMessage(channel, ret)
                return
            elif command == "{0}exec".format(commandChar):
                try:
                    exec(" ".join(text[4:]))
                except Exception as e:
                    SendMessage(channel, str(type(e)) + ":" + str(e))
                return
            elif command == "{0}quit".format(commandChar):
                SocketSend(irc, "QUIT :{0}\n".format(quitMessage))
                irc.close()
                quit()

        #actual commands here
        for mod in commands:
            for i in commands[mod]:
                if command == "{0}{1}".format(commandChar, i[0]) or command == "{0}{1}".format(botNick, i[0]):
                    i[1](username, hostmask, channel, text[4:])
                    return

while True:
    try:
        Connect()
        main()
        sleep(20)
    except KeyboardInterrupt:
        Print("Keyboard inturrupt, bot shut down")
        break
    except Exception:
        PrintError()
        Print("A strange error occured, reconnecting in 10 seconds")
        sleep(10)
        pass
