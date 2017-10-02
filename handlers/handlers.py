import sys

import log
from .user import User
from .server import Server
from .actions import Actions


class Events(User, Server, Actions):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config
        self.userdb = self.bot.userdb
        super(Events, self).__init__()

    def on_all(self, event, irc, arguments):
        if event.raw.find("%") == -1:
            log.debug(event.raw)

    def on_error(self, event, irc):
        log.error(" ".join(event.arguments))
        if " ".join(event.arguments).startswith("Closing Link"):
            self.bot.web.stop()
            self.userdb.flush()
            self.bot.db_job.stop()
            sys.exit(1)

    # Numeric events
    @staticmethod
    def on_endofmotd(event, irc):
        log.info("Received MOTD from network")

    @staticmethod
    def on_welcome(event, irc):
        log.info("Connected to network")
