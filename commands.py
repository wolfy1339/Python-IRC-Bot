import math
import time
import os
import re
from utils import add_cmd, commands, PY3, PrintError
import logging


@add_cmd("calc", alias=["math"], minArgs=1)
def calc(bot, event, irc, args):
    """Insert help text here"""
    safe_dict = {
        "sqrt": math.sqrt,
        "pow": math.pow,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "abs": abs,
        "log": math.log,
        "fact": math.factorial,
        "factorial": math.factorial
    }

    try:
        constant = {
           "e": str(math.e),
           "pi": str(math.pi),
        }

        for c in constant:
            m = args.replace("){0}".format(c), ") * {0}".format(constant[c]))
            p = re.compile(r'([:]?\d*\.\d+|\d+){0}'.format(c))
            subst = "\\1 * " + constant[c]
            m = re.sub(p, subst, m)
            m = re.sub('\\b{0}\\b'.format(c), constant[c], m)

        output = format(eval(m, {"__builtins__": None}, safe_dict), ",d")
        irc.reply(event, "The answer is: {0}".format(output))
    except ArithmeticError:
        irc.reply(event, "\x034Number undefined or too large.")
    except ValueError:
        irc.reply(event, "\x034Invalid Input")


@add_cmd("echo", minArgs=1)
def echo(bot, event, irc, args):
    """Help text"""
    irc.reply(event, args)


@add_cmd("ping", minArgs=0)
def ping(bot, event, irc, args):
    """Help text"""
    irc.reply(event, "PONG!")


@add_cmd("join", admin=True, minArgs=1)
def join(bot, event, irc, args):
    """Help text"""
    irc.join(args)


@add_cmd("part", alias=["leave"], admin=True, minArgs=1)
def part(bot, event, irc, args):
    """Help text"""
    if args is not None:
        irc.part(args)
    else:
        irc.part(event.target)


@add_cmd("ban", admin=True, minArgs=1)
def ban(bot, event, irc, args):
    """Help text"""
    irc.ban(args)


@add_cmd("unban", admin=True, minArgs=1)
def unban(bot, event, irc, args):
    """Help text"""
    irc.unban(args)


@add_cmd("op", admin=True, minArgs=0)
def op(bot, event, irc, args):
    """Help text"""
    if args is not None:
        irc.op(event.target, args)
    else:
        irc.op(event.target, event.source.nick)


@add_cmd("deop", admin=True, minArgs=0)
def deop(bot, event, irc, args):
    """Help text"""
    if args is not None:
        irc.deop(event.target, args)
    else:
        irc.deop(event.target, event.source.nick)


@add_cmd("voice", admin=True, minArgs=0)
def voice(bot, event, irc, args):
    if args is not None:
        irc.voice(event.target, args)
    else:
        irc.voice(event.target, event.source.nick)


@add_cmd("unvoice", admin=True, minArgs=0)
def unvoice(bot, event, irc, args):
    if args is not None:
        irc.unvoice(event.target, args)
    else:
        irc.unvoice(event.target, event.source.nick)


@add_cmd("nick", owner=True, minArgs=1)
def nick(bot, event, irc, args):
    bot.config['nickname'] = args
    irc.nick(args)


@add_cmd("log.level", admin=True, minArgs=1)
def logLevel(bot, event, irc, args):
    if args == "debug":
        level = logging.DEBUG
    elif args == "info":
        level = logging.INFO
    elif args == "error":
        level = logging.ERROR
    elif args == "warning":
        level = logging.WARNING
    elif args == "critical":
        level = logging.CRITICAL
    else:
        level = logging.INFO # Default logging level
        irc.reply(event, "Invalid log level {0}".format(args))
    logging.getLogger().setLevel(level)


@add_cmd("quit", admin=True, minArgs=0)
def Quit(bot, event, irc, args):
    """(\x02quit <text>\x0F) -- Exits the bot with the QUIT message <text>."""
    args = "zIRC - https://github.com/itslukej/zirc" if not args else args
    irc.quit(args)
    time.sleep(1)
    os._exit(0)


@add_cmd("help", minArgs=0)
def Help(bot, event, irc, args):
    """Help text"""
    if args:
        try:
            irc.reply(event, "Usage: {0}".format(commands[args]['function'].__doc__))
        except KeyError:
            irc.reply(event, "Invalid command {0}".format(args))
    else:
        irc.reply(event, "Usage: {0}".format(commands["help"]['function'].__doc__))


@add_cmd("list", minArgs=0, alias=["ls"])
def List(bot, event, irc, args):
    """Help text"""
    irc.reply(event, ", ".join(sorted(list(commands.keys()))))


@add_cmd("reload", admin=True)
def Reload(bot, event, irc, args):
    """Help text"""
    if PY3:
        reload = __import__("importlib").reload

    if args in ['commands', 'utils']:
        try:
            reload(args)
            irc.reply(event, "Reloaded {0}".format(args))
        except ImportError:
            PrintError()
    else:
        irc.reply(event, "Wrong module name")
