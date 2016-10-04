import math
import time
import os
import re
import logging
from utils import add_cmd, commands, cmd_list, aliases, PY3, PY34, PrintError
import config


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]


@add_cmd("calc", alias=["math"], minArgs=1)
def calc(bot, event, irc, args):
    """Command to do some math calculation"""
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
    """Responds with given text"""
    irc.reply(event, ' '.join(args))


@add_cmd("ping", minArgs=0)
def ping(bot, event, irc, args):
    """Help text"""
    irc.reply(event, "PONG!")


@add_cmd("join", admin=True, minArgs=1)
def join(bot, event, irc, args):
    """Joins given channel"""
    irc.join(args)


@add_cmd("part", alias=["leave"], admin=True, minArgs=0)
def part(bot, event, irc, args):
    """Parts the given channel or the current channel"""
    if len(args):
        irc.part(args[0])
    else:
        irc.part(event.target)


@add_cmd("ban", admin=True, minArgs=1)
def ban(bot, event, irc, args):
    """Bans a user"""
    if len(args):
        if len(args) > 1:
            if args[0].find("#") == -1:
                chunked = chunks(args[1:], 4)
                irc.mode(args[0], chunked, "+" + "b" * len(chunked))
            elif args[0].find("#") != -1:
                chunked = chunks(args, 4)
                irc.mode(event.target, chunked, "+" + "b" * len(chunked))
        else:
            irc.ban(event.target, args[0])
    else:
        irc.ban(event.target, event.source.nick)


@add_cmd("unban", admin=True, minArgs=1)
def unban(bot, event, irc, args):
    """Help text"""
    if len(args):
        if len(args) > 1:
            if args[0].find("#") == -1:
                chunked = chunks(args[1:], 4)
                irc.mode(args[0], chunked, "-" + "b" * len(chunked))
            elif args[0].find("#") != -1:
                chunked = chunks(args, 4)
                irc.mode(event.target, chunked, "-" + "b" * len(chunked))
        else:
            irc.unban(event.target, args[0])
    else:
        irc.unban(event.target, event.source.nick)


@add_cmd("op", admin=True, minArgs=0)
def op(bot, event, irc, args):
    """Help text"""
    if len(args):
        if len(args) > 1:
            if args[0].find("#") == -1:
                chunked = chunks(args[1:], 4)
                irc.mode(args[0], chunked, "+" + "o" * len(chunked))
            elif args[0].find("#") != -1:
                chunks(args, 4)
                irc.mode(event.target, chunked, "+" + "o" * len(chunked))
        else:
            irc.op(event.target, args[0])
    else:
        irc.op(event.target, event.source.nick)


@add_cmd("deop", admin=True, minArgs=0)
def deop(bot, event, irc, args):
    """Help text"""
    if len(args):
        if len(args) > 1:
            if args[0].find("#") == -1:
                chunked = chunks(args[1:], 4)
                irc.mode(args[0], chunked, "-" + "o" * len(chunked))
            elif args[0].find("#") != -1:
                chunked = chunks(args, 4)
                irc.mode(event.target, chunked, "-" + "o" * len(chunked))
        else:
            irc.deop(event.target, args[0])
    else:
        irc.deop(event.target, event.source.nick)


@add_cmd("voice", admin=True, minArgs=0)
def voice(bot, event, irc, args):
    """"Help text"""
    if len(args):
        if len(args) > 1:
            if args[0].find("#") == -1:
                irc.mode(args[0], chunks(args[1:], 4), "+vvvv")
            elif args[0].find("#") != -1:
                irc.mode(event.target, chunks(args, 4), "+vvvv")
        else:
            irc.deop(event.target, args[0])
    else:
        irc.voice(event.target, event.source.nick)


@add_cmd("unvoice", admin=True, minArgs=0)
def unvoice(bot, event, irc, args):
    """Help text"""
    if len(args):
        if len(args) > 1:
            if args[0].find("#") == -1:
                irc.mode(args[0], chunks(args[1:], 4), "-vvvv")
            elif args[0].find("#") != -1:
                irc.mode(event.target, chunks(args, 4), "-vvvv")
        else:
            irc.deop(event.target, args[0])
            irc.unvoice(event.target, args[0])
    else:
        irc.unvoice(event.target, event.source.nick)


@add_cmd("nick", owner=True, minArgs=1)
def nick(bot, event, irc, args):
    """Help text"""
    bot.config['nickname'] = args[0]
    irc.nick(args[0])


@add_cmd("log.level", admin=True, minArgs=1)
def logLevel(bot, event, irc, args):
    """Help text"""
    if args[0] == "debug":
        level = logging.DEBUG
    elif args[0] == "info":
        level = logging.INFO
    elif args[0] == "error":
        level = logging.ERROR
    elif args[0] == "warning":
        level = logging.WARNING
    elif args[0] == "critical":
        level = logging.CRITICAL
    else:
        level = logging.INFO # Default logging level
        irc.reply(event, "Invalid log level {0}".format(args))
    logging.getLogger().setLevel(level)


@add_cmd("config", admin=True, minArgs=1, alias=['cfg'])
def Config(bot, event, irc, args):
    """Help"""
    if len(args) > 1:
        eval("config.{0} = {1}".format(args[0], args[1]))
        irc.reply(event, "Set config.{0} to {1}".format(args[0], args[1]))
    else:
        irc.reply(event, eval("config.{0}".format(args[0])))

@add_cmd("quit", admin=True, minArgs=0)
def Quit(bot, event, irc, args):
    """(\x02quit <text>\x0F) -- Exits the bot with the QUIT message <text>."""
    args = "zIRC - https://github.com/itslukej/zirc" if not args else " ".join(args)
    irc.quit(args)
    time.sleep(1)
    os._exit(0)


@add_cmd("help", minArgs=0)
def Help(bot, event, irc, args):
    """Help text"""
    if len(args) >= 1:
        try:
            irc.reply(event, "Usage: {0}".format(commands[args[0]]['function'].__doc__))
        except KeyError:
            try:
                irc.reply(event, "Usage: {0}".format(aliases[args[0]]['function'].__doc__))
            except KeyError:
                irc.reply(event, "Invalid command {0}".format(args[0]))
    else:
        irc.reply(event, "Usage: {0}".format(commands["help"]['function'].__doc__))


@add_cmd("list", minArgs=0, alias=["ls"])
def List(bot, event, irc, args):
    """Help text"""
    irc.reply(event, ", ".join(sorted(cmd_list)))


@add_cmd("reload", admin=True)
def Reload(bot, event, irc, args):
    """Help text"""
    if PY34:
        reload = __import__("importlib").reload
    elif PY3:
        reload = __import__("imp").reload

    if args[0] in ['commands', 'utils', 'config']:
        try:
            reload(eval(args[0]))
            irc.reply(event, "Reloaded {0}".format(args[0]))
        except ImportError:
            PrintError(irc, event)
    else:
        irc.reply(event, "Wrong module name")
