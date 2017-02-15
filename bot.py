from os import path
import socket
import ssl

import commands
import config
import handlers
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

        self.events = handlers.Events(self)

    def removeEntry(self, event, nick):
        try:
            del self.userdb[event.target][nick]
        except KeyError:
            for i in self.userdb[event.target].values():
                if i['host'] == event.source.host:
                    del self.userdb[event.target][i['hostmask'].split("!")[0]]
                    break

    def addEntry(self, channel, nick, hostmask, host, account):
        self.userdb[channel][nick] = {
            'hostmask': hostmask,
            'host': host,
            'account': account
        }

    def on_all(self, event, irc, arguments):
        if event.raw.startswith("ERROR"):
            log.error(" ".join(event.arguments))
        else:
            try:
                getattr(self.events, "on_" + event.type)(event, irc, arguments)
            except AttributeError:
                try:
                    getattr(self.events, "on_" + event.text_type)(event, irc, arguments)
                except AttributeError:
                    utils.PrintError(irc, event)

            if event.raw.find("%") == -1:
                log.debug(event.raw)
Bot()
