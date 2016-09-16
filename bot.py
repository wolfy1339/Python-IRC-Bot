import zirc
import ssl
import socket
import utils
import commands

class Bot(zirc.Client):
    def __init__(self):
        self.connection = zirc.Socket(family=socket.AF_INET6,
                                      wrapper=ssl.wrap_socket)
        self.config = zirc.IRCConfig(host="irc.freenode.net",
                                     port=6697,
                                     nickname="zIRCBot2",
                                     ident="zirc",
                                     realname="A zIRC bot",
                                     channels=["##wolfy1339"],
                                     sasl_user="BigWolfy1339",
                                     sasl_pass="")

        self.connect(self.config)
        self.start()

    def on_ctcp(irc, raw):
        print(raw)

    def on_privmsg(bot, event, irc):
        utils.call_command(bot, event, irc)

Bot()
