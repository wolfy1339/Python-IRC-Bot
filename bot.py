import zirc
import ssl
import socket
import utils
import commands


debug = False

class Bot(zirc.Client):
    def __init__(self):
        self.connection = zirc.Socket(family=socket.AF_INET6,
                                      wrapper=ssl.wrap_socket)
        self.config = zirc.IRCConfig(host="chat.freenode.net",
                                     port=6697,
                                     nickname="zIRCBot2",
                                     ident="zirc",
                                     realname="A zIRC bot",
                                     channels=["##wolfy1339", "##powder-bots"],
                                     sasl_user="BigWolfy1339",
                                     sasl_pass="")

        self.connect(self.config)
        self.start()

    @staticmethod
    def on_ctcp(irc, raw):
        utils.print_(raw, flush=True)

    @classmethod
    def on_privmsg(self, event, irc, arguments):
        if " ".join(arguments).startswith("?"):
            utils.call_command(self, event, irc, arguments)

    @staticmethod
    def on_all(event, irc):
        if debug:
            utils.print_(event.raw, flush=True)

    @staticmethod
    def on_send(event, irc):
        if debug:
            utils.print_(event.raw, flush=True)

    @classmethod
    def on_nicknameinuse(self, event, irc):
        irc.nick(self.config['nickname'] + "_")

Bot()
