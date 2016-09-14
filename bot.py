import zirc
import ssl
import socket
import os


class Bot(zirc.Client):
    def __init__(self):
        self.connection = zirc.Socket(family=socket.AF_INET6,
                                      wrapper=ssl.wrap_socket)
        self.config = zirc.IRCConfig(host="irc.freenode.net",
                                     port=6697,
                                     nickname="wolfyzIRCBot",
                                     ident="zirc",
                                     realname="A zIRC bot",
                                     channels=["##wolfy1339"],
                                     sasl_user="BigWolfy1339",
                                     sasl_pass="")

        self.connect(self.config)
        self.start()

    def on_ctcp(irc, raw):
        print(raw)
    def on_privmsg(self, event, irc):
        privmsg = event.target == self.config['nickname']
        target = "a private message" if privmsg else event.target
        arguments = " ".join(event.arguments)
        if arguments.startswith("?help"):
            args = arguments.split("?help")[1].strip()
            if args == "quit" or args == "?quit":
                irc.reply(event, "?quit <message>")
            else:
                irc.reply(event, "Invalid command {}".format(arguments.split("?help")[1].strip()))
        elif arguments.startswith("?quit"):
            print("{} called quit in {}".format(event.source.nick, target))
            irc.quit(arguments.split("?quit")[1].strip())
            os._exit(1)
        elif arguments.startswith("?ping"):
            print("{} called ping in {}".format(event.source.nick, target))
            irc.reply(event, "PONG!")
        elif arguments.startswith("?join"):
            print("{} called join in {}".format(event.source.nick, target))
            irc.join(arguments.split("?join")[1].strip())
        elif arguments.startswith("?part"):
            print("{} called part in {}".format(event.source.nick, target))
            irc.part(arguments.split("?join")[1].strip())
        elif arguments.startswith("?ban"):
            irc.ban(event.target, arguments.split("?ban")[1].strip())
        elif arguments.startswith("?echo"):
            irc.reply(event, arguments.split("?echo")[1].strip())
        else:
            irc.reply(event, "Invalid command {}".format(arguments.strip()))
        print(event.raw)


Bot()
