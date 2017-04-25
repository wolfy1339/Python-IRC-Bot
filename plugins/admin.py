import os
import time

from zirc.util import repl
import config
import log
from utils.util import add_cmd
import utils


@add_cmd("eval", alias=['py', '>>'], min_args=1, owner=True, hide=True)
def Eval(bot, event, irc, args):
    """Admin console"""
    console = repl.Repl({'self': bot, 'bot': bot, 'irc': irc, 'event': event})
    try:
        irc.reply(event, console.run(" ".join(args)))
    except Exception as e:
        irc.reply(event, "{0}: {1}".format(e.__class__.__name__, e.args[0]))
        utils.util.print_error(irc, event)


@add_cmd("nick", owner=True, min_args=1)
def nick(bot, event, irc, args):
    """<nick>
    Changes the bot's nickname"""
    bot.config['nickname'] = args[0]
    irc.nick(args[0])


@add_cmd("log.level", admin=True, min_args=1)
def logLevel(bot, event, irc, args):
    """<level>
    Changes the logging level"""
    if args[0] == "debug":
        level = 10
        irc.reply(event, "Set log level to {0}".format(args[0]))
    elif args[0] == "info":
        level = 20
        irc.reply(event, "Set log level to {0}".format(args[0]))
    elif args[0] == "error":
        level = 30
        irc.reply(event, "Set log level to {0}".format(args[0]))
    elif args[0] == "warning":
        level = 40
        irc.reply(event, "Set log level to {0}".format(args[0]))
    elif args[0] == "critical":
        level = 50
        irc.reply(event, "Set log level to {0}".format(args[0]))
    else:
        level = config.logLevel  # Default logging level
        irc.reply(event, "Invalid log level {0}".format(args))
    log.setLevel(level)


@add_cmd("config", admin=True, min_args=1, alias=['cfg'])
def Config(bot, event, irc, args):
    """<nick>
    Changes or displays a config variable"""
    if len(args) > 1:
        if hasattr(config, args[0]):
            setattr(config, args[0], args[1])
            irc.reply(event, "Set config.{0} to {1}".format(args[0], args[1]))
        else:
            irc.reply(event, "Invalid config variable {}".format(args[0]))
    else:
        if hasattr(config, args[0]):
            if args[0] == 'password' and event.target.startswith('#'):
                irc.reply(event, config.secretEntry)
            else:
                irc.reply(event, repr(getattr(config, args[0])))
        else:
            irc.reply(event, "Invalid config variable {}".format(args[0]))


@add_cmd("quit", admin=True, min_args=0)
def Quit(bot, event, irc, args):
    """<text>
    Exits the bot with the QUIT message <text>."""
    irc.quit("zIRC - https://github.com/itslukej/zirc" if (
        not args) else " ".join(args))
    time.sleep(1)
    os._exit(0)


@add_cmd("reload", admin=True, min_args=1, hide=True)
def Reload(bot, event, irc, args):
    """Help text"""
    if utils.util.PY34:
        reload = __import__("importlib").reload
    elif utils.util.PY3:
        reload = __import__("imp").reload
    elif utils.util.PY2:
        reload = __builtins__.reload

    if args[0] in ['commands', 'utils', 'config', 'log']:
        try:
            reload(__import__(args[0]))
            irc.reply(event, "Reloaded {0}".format(args[0]))
        except ImportError:
            utils.util.print_error(irc, event)
    else:
        irc.reply(event, "Wrong module name")


@add_cmd("flushq", alias=['flush'], min_args=0, admin=True)
def flush(bot, event, irc, args):
    bot.fp.irc_queue = []
    irc.reply(event, "Cleared IRC queue")


@add_cmd("ignore", min_args=1, admin=True)
def add_ignore(bot, event, irc, args):
    """<host> [<duration|random>] [<channel>]
    Adds an ignore for the specified host"""
    utils.ignores.add_ignore(irc, event, args)
