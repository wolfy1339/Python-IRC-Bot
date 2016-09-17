import math
import time
import os
import re
from utils import add_cmd, commands

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
        t = args.replace("e", math.e).replace("pi", math.pi)
        r = re.match("[0-9]!", t).groups()
        for i in r:
            t = t.replace(i, "fact(" + i.split("!")[0] + ")")
        a = format(eval(t, {"__builtins__": None}, safe_dict), ",d")
        irc.reply(event, "The answer is: {0}".format(a))
    except ArithmeticError:
        irc.reply(event, "\x034Number undefined or too large.")
    except Exception:
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

@add_cmd("quit", admin=True)
def Quit(bot, event, irc, args):
    """(\x02quit <text>\x0F) -- Exits the bot with the QUIT message <text>."""
    irc.quit(args)
    time.spleep(1)
    os._exit(1)

@add_cmd("help")
def Help(bot, event, irc, args):
    """Help text"""
    try:
        irc.reply(event, "Usage: {}".format(commands[args][0].__doc__))
    except KeyError:
        if args:
            irc.reply(event, "Invalid command {}".format(args))
        else:
            irc.reply(event, "Usage: {}".format(commands["help"][0].__doc__))

@add_cmd("list", alias="ls")
def List(bot, event, irc, args):
    """Help text"""
    irc.reply(event, ", ".join(commands.keys()))
