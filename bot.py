from os import path
import socket
import ssl
import sys

import commands
import config
import events
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
        events = events.Events(self)
        for i in dir(events):
            func = getattr(events, i)
            if callable(func) and not i.startswith("__"):
                setattr(self, i, func)

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


Bot()
