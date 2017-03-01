from os import path
import socket
import ssl

import config
import handlers
import utils
import zirc


class Bot(zirc.Client):
    def __init__(self):
        self.userdb = {}
        for i in config.channels:
            self.userdb[i] = {}

        self.events = handlers.Events(self)
        # Non numeric events
        self.on_all = self.events.on_all
        self.on_privmsg = self.events.on_privmsg
        self.on_ctcp = self.events.on_ctcp
        self.on_send = self.events.on_send
        self.on_nick = self.events.on_nick
        self.on_quit = self.events.on_quit
        self.on_kick = self.events.on_kick
        self.on_part = self.events.on_part
        self.on_join = self.events.on_join
        self.on_invite = self.events.on_invite
        # Numeric events
        self.on_unavailresource = self.events.on_unavailresource
        self.on_nicknameinuse = self.events.on_nicknameinuse
        self.on_bannedfromchan = self.events.on_bannedfromchan
        self.on_endofmotd = self.events.on_endofmotd
        self.on_welcome = self.events.on_welcome
        self.on_whoreply = self.events.on_whoreply
        self.on_whospcrpl = self.events.on_whospcrpl
        self.on_315 = self.events.on_315

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
