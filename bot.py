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
            print("{} called quit in {}".format(event.source.nick, target))
            irc.quit(arguments.split("?quit")[1].strip())
            os._exit(1)
        elif arguments.startswith("?ping"):
            print("{} called ping in {}".format(event.source.nick, target))
            irc.reply("PONG!")
        elif arguments.startswith("?join"):
            print("{} called join in {}".format(event.source.nick, target))
            irc.join(arguments.split("?join")[1].strip())
        print(event.raw)


Bot()
