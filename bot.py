from os import path
import socket
import ssl
import threading

import config
import handlers
import utils
import zirc
from zirc.wrappers import connection_wrapper


class Bot(zirc.Client):
    def __init__(self):
        self.irc = connection_wrapper(self)
        self.userdb = utils.database.Database(config.channels,
                                              self.irc)

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
            'TIME': __import__('time').localtime,
            'FINGER': "Don't finger me",
            'USERINFO': 'An IRC bot built using zIRC on Python',
            'SOURCE': 'https://github.com/wolfy1339/Python-IRC-Bot'
        }
        # Event handlers
        self.events = handlers.Events(self)
        for i in dir(self.events):
            func = getattr(self.events, i)
            if callable(func) and not i.startswith("__"):
                setattr(self, i, func)
        self.connect(self.config, certfile=path.abspath("user.pem"))
        utils.web.irc = self.irc
        utils.web.bot = self
        threading.Thread(target=utils.web.app.run, args=('0.0.0.0')).start()
        threading.Thread(target=self.start).start()

Bot()
