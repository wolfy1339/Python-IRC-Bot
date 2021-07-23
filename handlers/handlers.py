from typing import List
from zirc import event, wrappers
from bot import Bot
import sys

import log
from .user import User
from .server import Server
from .actions import Actions
from utils.irc import strip_colours


class Events(User, Server, Actions):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.config = self.bot.config
        self.userdb = self.bot.userdb
        super(Events, self).__init__()

    def on_all(self, event: event.Event, irc: wrappers.connection_wrapper, arguments: List[str]):
        if event.raw.find("%") == -1:
            log.debug(strip_colours(event.raw))

    def on_error(self, event: event.Event, irc: wrappers.connection_wrapper):
        log.error(" ".join(event.arguments))
        if " ".join(event.arguments).startswith("Closing Link"):
            self.bot.fp.irc_queue = []
            self.bot.web.stop()
            self.userdb.flush()
            self.bot.db_job.stop()
            sys.exit(1)

    # Numeric events
    @staticmethod
    def on_endofmotd(event: event.Event, irc: wrappers.connection_wrapper):
        log.info("Received MOTD from network")

    @staticmethod
    def on_welcome(event: event.Event, irc: wrappers.connection_wrapper):
        log.info("Connected to network")

    def on_324(self, event: event.Event, irc: wrappers.connection_wrapper):
        self.userdb[event.target]['modes'] = list(event.arguments[0][1:])
