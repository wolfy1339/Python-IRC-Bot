import socket
import ssl

import commands
import config
import log
import utils
import zirc


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
            log.error(" ".join(event.arguments))
        else:
            log.debug(event.raw)

    @staticmethod
    def on_ctcp(irc, raw):
        log.info("Received CTCP reply " + raw)

    def on_privmsg(self, event, irc, arguments):
        if " ".join(arguments).startswith(config.commandChar):
            utils.call_command(self, event, irc, arguments)

    @staticmethod
    def on_send(data):
        log.debug(data)

    def on_kick(self, event, irc):
        nick = event.raw.split(" ")[3]
        if nick == self.config['nickname']:
            log.warning("Kicked from %s, trying to re-join", event.target)
            irc.join(event.target)

    def on_join(self, event, irc):
        log.info("Joining %s", event.target)
        irc.send("WHO {0} nuhs%nhu".format(event.target))

    def on_invite(self, event, irc):
        if utils.checkPerms(event.source.host, trusted=True):
            hostmask = event.source.hostmask
            log.info("Invited to %s by %s", event.target, hostmask)
            irc.join(event.target)

    # Numeric events
    def on_nicknameinuse(self, event, irc):
        log.error("Nick already in use, trying alternative")
        irc.nick(self.config['nickname'] + "_")

    @staticmethod
    def on_bannedfromchan(event, irc):
        s = event.raw.split(" ")
        channel = s[3]
        irc.notice("wolfy1339", "Banned from {0}".format(channel))
        log.warning("Banned from %s", channel)

    def on_endofmotd(event, irc):
        log.info("Received MOTD from network")

    def on_welcome(event, irc):
        log.info("Connected to network")

    def on_whoreply(self, event, irc):
        (host, ident, nick) = event.arguments[1:3] + event.arguments[4]
        hostmask = "{0}!{1}@{2}".format(nick, ident, host)
        self.userdb[nick] = {
            'hostmask': hostmask,
            'host': host,
            'account': None
        }

    def on_whospcrpl(self, event, irc):
        (ident, host, nick) = event.arguments
        hostmask = "{0}!{1}@{2}".format(nick, ident, host)
        self.userdb[nick] = {
            'hostmask': hostmask,
            'host': host,
            'account': None
        }

    def on_315(self, event, irc):
        log.info("Received end of WHO reply from network")

Bot()
