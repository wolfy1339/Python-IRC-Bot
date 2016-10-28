import math
import time
import os
import re
import logging
from utils import add_cmd
import utils
import config


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]


def setMode(event, irc, args, mode):
    if args[0].find("#") == -1:
        for i in chunks(args[1:], 4):
            modes = "".join(mode[1:]) * len(i)
            irc.mode(args[0], " ".join(i), "".join(mode[:1]) + modes)
    else:
        for i in chunks(args, 4):
            modes = "".join(mode[1:]) * len(i)
            irc.mode(event.target, " ".join(i), "".join(mode[:1]) + modes)


@add_cmd("calc", alias=["math"], minArgs=1)
def calc(bot, event, irc, args):
    """Command to do some math calculation"""
    arguments = "".join(args)
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
            m = arguments.replace("){0}".format(c), ") * {0}".format(constant[c]))
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


@add_cmd("eval", alias=['py'], minArgs=1, owner=True, hide=True)
def repl(bot, event, irc, args):
    """Help text"""
    irc.reply(event, eval(" ".join(args)))


@add_cmd("echo", minArgs=1)
def echo(bot, event, irc, args):
    """Responds with given text"""
    irc.reply(event, ' '.join(args))


@add_cmd("rainbow", minArgs=1)
def rainbow(bot, event, irc, args):
    """Responds with given text colored in rainbow"""
    irc.reply(event, ' '.join(args), colour="rainbow")


@add_cmd("ping", minArgs=0)
def ping(bot, event, irc, args):
    """Help text"""
    irc.reply(event, "PONG!")


@add_cmd("join", admin=True, minArgs=1)
def join(bot, event, irc, args):
    """Joins given channel"""
    irc.join(args[0])


@add_cmd("part", alias=["leave"], admin=True, minArgs=0)
def part(bot, event, irc, args):
    """Parts the given channel or the current channel"""
    if len(args):
        irc.part(args[0])
    else:
        irc.part(event.target)

@add_cmd("cycle", alias=["rejoin"], admin=True, minArgs=0)
def cycle(bot, event, irc, args):
    if len(args):
        irc.part(args[0])
        irc.join(args[0])
    else:
        irc.part(event.target)
        irc.join(event.target)

@add_cmd("ban", admin=True, minArgs=1)
def ban(bot, event, irc, args):
    """Bans a user"""
    if len(args) > 1:
        setMode(event, irc, args, "+b")
    else:
        irc.ban(event.target, args[0])


@add_cmd("unban", admin=True, minArgs=1)
def unban(bot, event, irc, args):
    """Help text"""
    if len(args) > 1:
        setMode(event, irc, args, "-b")
    else:
        irc.unban(event.target, args[0])


@add_cmd("op", admin=True, minArgs=0)
def op(bot, event, irc, args):
    """Help text"""
    if len(args):
        if len(args) > 1:
            setMode(event, irc, args, "+o")
        else:
            irc.op(event.target, args[0])
    else:
        irc.op(event.target, event.source.nick)


@add_cmd("deop", admin=True, minArgs=0)
def deop(bot, event, irc, args):
    """Help text"""
    if len(args):
        if len(args) > 1:
            setMode(event, irc, args, "-o")
        else:
            irc.deop(event.target, args[0])
    else:
        irc.deop(event.target, event.source.nick)


@add_cmd("voice", admin=True, minArgs=0)
def voice(bot, event, irc, args):
    """"Help text"""
    if len(args):
        if len(args) > 1:
            setMode(event, irc, args, "+v")
        else:
            irc.deop(event.target, args[0])
    else:
        irc.voice(event.target, event.source.nick)


@add_cmd("unvoice", admin=True, minArgs=0)
def unvoice(bot, event, irc, args):
    """Help text"""
    if len(args):
        if len(args) > 1:
            setMode(event, irc, args, "-v")
        else:
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
        level = logging.INFO  # Default logging level
        irc.reply(event, "Invalid log level {0}".format(args))
    logging.getLogger().setLevel(level)


@add_cmd("config", admin=True, minArgs=1, alias=['cfg'])
def Config(bot, event, irc, args):
    """Help"""
    if len(args) > 1:
        if hasattr(config, args[0]):
            setattr(config, args[0], args[1])
            irc.reply(event, "Set config.{0} to {1}".format(args[0], args[1]))
        else:
            irc.reply(event, "Invalid config variable {}".format(args[0]))
    else:
        if hasattr(config, args[0]):
            irc.reply(event, getattr(config, args[0]))
        else:
            irc.reply(event, "Invalid config variable {}".format(args[0]))


@add_cmd("quit", admin=True, minArgs=0)
def Quit(bot, event, irc, args):
    """(\x02quit <text>\x0F) -- Exits the bot with the QUIT message <text>."""
    irc.quit("zIRC - https://github.com/itslukej/zirc" if (
        not args) else " ".join(args))
    time.sleep(1)
    os._exit(0)


@add_cmd("help", minArgs=0)
def Help(bot, event, irc, args):
    """Help text"""
    if len(args) >= 1:
        try:
            doc = utils.commands[args[0]]['func'].__doc__
            irc.reply(event, "Usage: {0}".format(doc))
        except KeyError:
            try:
                doc = utils.aliases[args[0]]['func'].__doc__
                irc.reply(event, "Usage: {0}".format(doc))
            except KeyError:
                irc.reply(event, "Invalid command {0}".format(args[0]))
    else:
        doc = utils.commands["help"]['func'].__doc__
        irc.reply(event, "Usage: {0}".format(doc))


@add_cmd("list", minArgs=0, alias=["ls"])
def List(bot, event, irc, args):
    """Help text"""
    if len(args) and args[0] == "alias":
        irc.reply(event, ", ".join(utils.alias_list))
    else:
        irc.reply(event, ", ".join(utils.cmd_list))


@add_cmd("reload", admin=True, minArgs=1)
def Reload(bot, event, irc, args):
    """Help text"""
    if utils.PY34:
        reload = __import__("importlib").reload
    elif utils.PY3:
        reload = __import__("imp").reload

    if args[0] in ['commands', 'utils', 'config']:
        try:
            reload(eval(args[0]))
            irc.reply(event, "Reloaded {0}".format(args[0]))
        except ImportError:
            utils.PrintError(irc, event)
    else:
        irc.reply(event, "Wrong module name")


@add_cmd("host", minArgs=0)
def hostmask(bot, event, irc, args):
    """Replies with your host"""
    irc.reply(event, event.source.host)


@add_cmd("perms", minArgs=0)
def permissions(bot, event, irc, args):
    """Replies with your permission level"""
    host = event.source.host

    if host in config.owner:
        perms = 'owner'
    elif host in config.admins:
        perms = 'admin'
    elif host in config.trusted:
        perms = 'trusted'
    else:
        perms = 'User'

    irc.reply(event, perms)
