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
            if event.raw.find("%") == -1:
                log.debug(event.raw)

    @staticmethod
    def on_ctcp(irc, raw):
        log.info("Received CTCP reply " + raw)

    def on_privmsg(self, event, irc, arguments):
        if " ".join(arguments).startswith(config.commandChar):
            utils.call_command(self, event, irc, arguments)

    @staticmethod
    def on_send(data):
        if data.find("%") == -1:
            log.debug(data)

    def on_kick(self, event, irc):
        nick = event.raw.split(" ")[3]
        if nick == self.config['nickname']:
            log.warning("Kicked from %s, trying to re-join", event.target)
            irc.join(event.target)

    def on_part(self, event, irc):
        requested = "".join(event.arguments).startswith("requested")
        if event.source.nick == self.config['nickname'] and requested:
            log.warning("Removed from %s, trying to re-join", event.target)
            irc.join(event.target)
        else:
            try:
                self.userdb[event.target].pop(event.source.nick)
            except KeyError:
                for i in self.userdb:
                    if i['host'] == event.source.host:
                        self.userdb[event.target].pop(i['hostmask'].split("!")[0])

    def on_join(self, event, irc):
        if event.source.nick == self.config['nickname']:
            log.info("Joining %s", event.target)
            irc.send("WHO {0} nuhs%nhuac".format(event.target))
        else:
            irc.send("WHO {0}".format(event.source.nick))

    def on_invite(self, event, irc):
        if utils.checkPerms(event.source.host, trusted=True):
            hostmask = event.source.host
            log.info("Invited to %s by %s", event.arguments[1], hostmask)
            irc.join(event.arguments[1])

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
        (ident, host, nick) = event.arguments[1:3] + event.arguments[4:5]
        channel = event.arguments[0]
        hostmask = "{0}!{1}@{2}".format(nick, ident, host)
        if nick != "ChanServ":
            try:
                self.userdb[channel][nick] = {
                    'hostmask': hostmask,
                    'host': host,
                    'account': ''.join(host.split("/")[:-1])
                }
            except KeyError:
                self.userdb[channel] = {}
                self.userdb[channel][nick] = {
                    'hostmask': hostmask,
                    'host': host,
                    'account': ''.join(host.split("/")[:-1])
                } 

    def on_whospcrpl(self, event, irc):
        (ident, host, nick) = event.arguments[1:4]
        hostmask = "{0}!{1}@{2}".format(nick, ident, host)
        channel = event.arguments[0]
        account = event.arguments[4]
        if nick != "ChanServ":
            try:
                self.userdb[channel][nick] = {
                    'hostmask': hostmask,
                    'host': host,
                    'account': account
                }
            except KeyError:
                self.userdb[channel] = {}
                self.userdb[channel][nick] = {
                    'hostmask': hostmask,
                    'host': host,
                    'account': account
                } 

    def on_315(self, event, irc):
        log.info("Received end of WHO reply from network")

Bot()
