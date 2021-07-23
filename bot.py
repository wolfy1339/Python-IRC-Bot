from os import path
import socket
import ssl
from os import getenv
from utils.database import Database, UserDB

import config
import utils
from utils import tasks
import zirc


class Bot(zirc.Client):
    def __init__(self):
        # zIRC
        self.connection = zirc.Socket(family=socket.AF_INET6,
                                      wrapper=ssl.wrap_socket)
        self.config = zirc.IRCConfig(host="irc.libera.chat",
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
        self.userdb: Database[str, dict[str, UserDB]] = utils.database.Database(self)
        utils.util.reload_handlers(self)
        self.connect(self.config, certfile=path.abspath("user.pem"))
        self.fp.sleep_time = 0.7
        self.fp.lines = 5

        utils.web.irc = zirc.wrappers.connection_wrapper(self)
        utils.web.bot = self
        try:
            kwargs = {
                'host': '0.0.0.0',
                'ssl_context': utils.web.ssl_context()
            }
        except FileNotFoundError:
            kwargs = {
                'host': '0.0.0.0'
            }
        if not getenv('DEV', '') == 'true':
            self.web = tasks.run(utils.web.app.run, daemon=True, kwargs=kwargs)
        self.db_job = tasks.run_every(600, self.userdb.flush, daemon=True)


x = Bot()
try:
    x.start()
except KeyboardInterrupt:
    x.fp.irc_queue = []
    x.irc.quit("KeyboardInterrupt")
    utils.web.app.stop()
    x.web.stop()
    x.userdb.flush()
    x.bot.db_job.stop()
    x.socket.close()
    __import__("sys").exit(1)
