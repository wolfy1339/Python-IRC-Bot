import logging
import socket
import ssl

import commands
import config
import utils
import zirc

logging.basicConfig(format=config.logFormat,
                    datefmt=config.timestampFormat,
                    level=config.logLevel,
                    filename="messages.log",
                    filemode="w")


class Bot(zirc.Client):
    def __init__(self):
        self.userdb = {}
        # zIRC
        self.connection = zirc.Socket(family=socket.AF_INET6,
                                      wrapper=ssl.wrap_socket)
        self.config = zirc.IRCConfig(host="chat.freenode.net",
                                     port=6697,
                                     nickname="zIRCBot2",
                                     ident="zirc",
                                     realname="A zIRC bot",
                                     channels=config.channels,
                                     caps=config.caps)

        self.connect(self.config)
        self.start()

    # Non-numeric events
    @staticmethod
    def on_all(event, irc):
        if event.raw.startswith("ERROR"):
            logging.error(event.arguments)
        else:
            logging.debug(event.raw)

    @staticmethod
    def on_ctcp(irc, raw):
        logging.info("Received CTCP reply " + raw)

    def on_privmsg(self, event, irc, arguments):
        if " ".join(arguments).startswith(config.commandChar):
            utils.call_command(self, event, irc, arguments)

    @staticmethod
    def on_send(data):
        logging.debug(data)

    def on_kick(self, event, irc):
        logging.warning("Kicked from %s, trying to re-join", event.target)
        irc.join(event.target)

    def on_join(self, event, irc):
        logging.info("Joining %s", event.target)
        irc.send("WHO {0} nuhs%nhu".format(event.target))

    def on_invite(self, event, irc):
        if utils.checkPerms(event.source.host, trusted=True):
            hostmask = event.source.hostmask
            logging.info("Invited to %s by %s", event.target, hostmask)
            irc.join(event.target)

    # Numeric events
    def on_nicknameinuse(self, event, irc):
        logging.error("Nick already in use, trying alternative")
        irc.nick(self.config['nickname'] + "_")

    @staticmethod
    def on_bannedfromchan(event, irc):
        s = event.raw.split(" ")
        channel = s[3]
        irc.notice("wolfy1339", "Banned from {0}".format(channel))
        logging.warning("Banned from %s", channel)

    def on_endofmotd(event, irc):
        logging.info("Received MOTD from network")

    def on_welcome(event, irc):
        logging.info("Connected to network")

    def on_whoreply(self, event, irc):
        (host, ident, nick) = event.arguments[1:3] + event.arguments[4]
        hostmask = "{0}!{1}@{2}".format(nick, ident, host)
        self.userdb[nick] = {
            'hostmask': hostmask,
            'host': host,
            'account': None
        }

    def on_whospcrpl(self, event, irc):
        logging.info("Received WHO reply from network")
        (host, ident, nick) = event.arguments
        hostmask = "{0}!{1}@{2}".format(nick, ident, host)
        self.userdb[nick] = {
            'hostmask': hostmask,
            'host': host,
            'account': None
        }

    def on_315(self, event, irc):
        logging.info("Received end of WHO reply from network")

Bot()
