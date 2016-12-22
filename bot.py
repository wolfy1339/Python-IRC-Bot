from os import path
import socket
import ssl
import sys

import commands
import config
import log
import utils
import zirc


class Bot(zirc.Client):
    def __init__(self):
        self.userdb = {}
        for i in config.channels:
            self.userdb[i] = {}

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
        self.ctcp = {
            'VERSION': utils.version,
            'TIME': __import__('time').localtime(),
            'FINGER': "Don't finger me",
            'USERINFO': 'An IRC bot built using zIRC on Python',
            'SOURCE': 'https://github.com/wolfy1339/Python-IRC-Bot'
        }
        self.connect(self.config, certfile=path.abspath("user.pem"))
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
    def on_ctcp(irc, event, raw):
        log.info("Received CTCP reply " + raw)

    def on_privmsg(self, event, irc, arguments):
        if " ".join(arguments).startswith(config.commandChar):
            utils.call_command(self, event, irc, arguments)

    @staticmethod
    def on_send(data):
        if data.find("%") == -1:
            log.debug(data)

    def on_nick(self, event, irc):
        nick = event.source.nick
        to_nick = event.arguments[0]
        for chan in self.userdb.keys():
            for u in self.userdb[chan].values():
                if u['host'] == event.source.host:
                    self.userdb[chan][to_nick] = self.userdb[chan][nick]
                    hostmask = self.userdb[chan][to_nick]['hostmask'].split("!")[1]
                    self.userdb[chan][to_nick]['hostmask'] = to_nick + '!' + hostmask
                    del self.userdb[chan][nick]
                    break
            break

    def on_quit(self, event, irc):
        nick = event.source.nick
        if nick == self.config['nickname']:
            sys.exit(1)
        else:
            for chan in self.userdb.keys():
                for u in self.userdb[chan].values():
                    if u['host'] == event.source.host:
                        del self.userdb[chan][nick]
                        break
                break

    def on_kick(self, event, irc):
        nick = event.raw.split(" ")[3]
        if nick == self.config['nickname']:
            log.warning("Kicked from %s, trying to re-join", event.target)
            irc.join(event.target)
        else:
            try:
                del self.userdb[event.target][nick]
            except KeyError:
                for i in self.userdb[event.target].values():
                    if i['host'] == event.source.host:
                        del self.userdb[event.target][i['hostmask'].split("!")[0]]
                        break

    def on_part(self, event, irc):
        requested = "".join(event.arguments).startswith("requested")
        if event.source.nick == self.config['nickname']:
            if requested:
                log.warning("Removed from %s, trying to re-join", event.target)
                irc.join(event.target)
            else:
                try:
                    del self.userdb[event.target][event.source.nick]
                except KeyError:
                    for i in self.userdb[event.target].values():
                        if i['host'] == event.source.host:
                            del self.userdb[event.target][i['hostmask'].split("!")[0]]
                            break
        else:
            try:
                del self.userdb[event.target][event.source.nick]
            except KeyError:
                for i in self.userdb[event.target].values():
                    if i['host'] == event.source.host:
                        del self.userdb[event.target][i['hostmask'].split("!")[0]]
                        break

    def on_join(self, event, irc):
        if event.source.nick == self.config['nickname']:
            log.info("Joining %s", event.target)
            self.userdb[event.target] = {}
            irc.send("WHO {0} nuhs%nhuac".format(event.target))
        else:
            irc.send("WHO {0} nuhs%nhuac".format(event.source.nick))

    @staticmethod
    def on_invite(event, irc):
        if utils.checkPerms(event.source.host, trusted=True):
            hostmask = event.source.host
            log.info("Invited to %s by %s", event.arguments[1], hostmask)
            irc.join(event.arguments[1])

    # Numeric events
    def on_unavailresource(self, event, irc):
        log.error("Nick unavailable, trying alternative")
        irc.nick(self.config['nickname'] + "_")
        self.config['nickname'] = self.config['nickname'] + "_"

    def on_nicknameinuse(self, event, irc):
        log.error("Nick already in use, trying alternative")
        irc.nick(self.config['nickname'] + "_")
        self.config['nickname'] = self.config['nickname'] + "_"

    @staticmethod
    def on_bannedfromchan(event, irc):
        s = event.raw.split(" ")
        channel = s[3]
        irc.notice("wolfy1339", "Banned from {0}".format(channel))
        log.warning("Banned from %s", channel)

    @staticmethod
    def on_endofmotd(event, irc):
        log.info("Received MOTD from network")

    @staticmethod
    def on_welcome(event, irc):
        log.info("Connected to network")

    def on_whoreply(self, event, irc):
        (ident, host, nick) = event.arguments[1:3] + event.arguments[4:5]
        channel = event.arguments[0]
        hostmask = "{0}!{1}@{2}".format(nick, ident, host)
        if nick != "ChanServ":
            self.userdb[channel][nick] = {
                'hostmask': hostmask,
                'host': host,
                'account': host.split("/")[-1].split('.')[-1]
            }

    def on_whospcrpl(self, event, irc):
        (ident, host, nick) = event.arguments[1:4]
        hostmask = "{0}!{1}@{2}".format(nick, ident, host)
        channel = event.arguments[0]
        account = event.arguments[4]
        if nick != "ChanServ":
            self.userdb[channel][nick] = {
                'hostmask': hostmask,
                'host': host,
                'account': account if account != "0" else None
            }

    @staticmethod
    def on_315(event, irc):
        log.info("Received end of WHO reply from network")

Bot()
