import zirc
import ssl
import socket
import utils
import commands
import logging
import config


logging.basicConfig(format=config.logFormat,
                    datefmt=config.timestampFormat,
                    level=config.logLevel)


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
                                     caps=zirc.Caps(zirc.Sasl(username="BigWolfy1339", password="")))

        self.connect(self.config)
        self.start()

    @staticmethod
    def on_ctcp(irc, raw):
        logging.info(raw)

    def on_privmsg(self, event, irc, arguments):
        if " ".join(arguments).startswith(config.commandChar):
            utils.call_command(self, event, irc, arguments)

    @staticmethod
    def on_all(event, irc):
        if event.raw.startswith("ERROR"):
            logging.error(event.raw)
        else:
            logging.debug(event.raw)

    @staticmethod
    def on_send(data):
        logging.debug(data)

    def on_nicknameinuse(self, event, irc):
        irc.nick(self.config['nickname'] + "_")

    @staticmethod
    def on_474(event, irc):
        s = ''.join(event.arguments).split(" ")
        channel = s[1]
        irc.notice("wolfy1339", "Banned from {0}".format(channel))
        logging.warning("%s from %s", ' '.join(s[2:]), channel)

Bot()
