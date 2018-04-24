from os import path
import socket
import ssl

import config
import utils
from utils import tasks
import zirc
from zirc.wrappers import connection_wrapper


class Bot(zirc.Client):
    def __init__(self):
        self.irc = connection_wrapper(self)
        self.userdb = utils.database.Database(self.irc)

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
        utils.util.reload_handlers(self)
        self.connect(self.config, certfile=path.abspath("user.pem"))
        utils.web.irc = self.irc
        self.fp.sleep_time = 0.7
        self.fp.lines = 5
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
        self.db_job = tasks.run_every(600, self.userdb.flush, daemon-True)

x = Bot()
try:
    x.start()
except KeyboardInterrupt:
    x.irc.quit("KeyboardInterrupt")
    utils.web.app.stop()
    x.web.stop()
    x.userdb.flush()
    x.bot.db_job.stop()
    sys.exit(1)
