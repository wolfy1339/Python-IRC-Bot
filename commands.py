import math
import time
import os
import re
from utils import add_cmd, commands, PY3


@add_cmd("calc", alias="math")
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


@add_cmd("echo")
def echo(bot, event, irc, args):
    """Help text"""
    irc.reply(event, args)


@add_cmd("ping")
def ping(bot, event, irc, args):
    """Help text"""
    irc.reply(event, "PONG!")


@add_cmd("join", admin=True)
def join(bot, event, irc, args):
    """Help text"""
    irc.join(args)


@add_cmd("part", alias="leave", admin=True)
def part(bot, event, irc, args):
    """Help text"""
    irc.part(args)


@add_cmd("ban", admin=True)
def ban(bot, event, irc, args):
    """Help text"""
    irc.ban(args)


@add_cmd("unban", admin=True)
def unban(bot, event, irc, args):
    """Help text"""
    irc.unban(args)


@add_cmd("op", admin=True)
def op(bot, event, irc, args):
    """Help text"""
    irc.op(event.target, args)


@add_cmd("deop", admin=True)
def deop(bot, event, irc, args):
    """Help text"""
    irc.deop(event.target, args)


@add_cmd("voice", admin=True)
def voice(bot, event, irc, args):
    irc.voice(event.target, args)


@add_cmd("unvoice", admin=True)
def unvoice(bot, event, irc, args):
    irc.unvoice(event.target, args)


@add_cmd("nick", owner=True)
def nick(bot, event, irc, args):
    irc.nick(args)


@add_cmd("quit", admin=True)
def Quit(bot, event, irc, args):
    """(\x02quit <text>\x0F) -- Exits the bot with the QUIT message <text>."""
    args = "zIRC - https://github.com/itslukej/zirc" if not args else args
    irc.quit(args)
    time.spleep(1)
    os._exit(0)


@add_cmd("help")
def Help(bot, event, irc, args):
    """Help text"""
    try:
        irc.reply(event, "Usage: {0}".format(commands[args].__doc__))
    except KeyError:
        if args:
            irc.reply(event, "Invalid command {0}".format(args))
        else:
            irc.reply(event, "Usage: {0}".format(commands["help"].__doc__))


@add_cmd("list", alias="ls")
def List(bot, event, irc, args):
    """Help text"""
    irc.reply(event, ", ".join(sorted(list(commands.keys()))))


@add_cmd("reload", admin=True)
def Reload(bot, event, irc, args):
    """Help text"""
    if __import__("sys").version_info[0] >= 3:
        reload = __import__("importlib").reload

    if args in ['commands', 'utils']:
        reload(args)
        irc.reply(event, "Reloaded {0}".format(args))
    else:
        irc.reply(event, "Wrong module name")
