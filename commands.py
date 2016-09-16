import math
import time
import os

@add_cmd("math", alias="calc")
def math(bot, event, irc, args):
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
        if args.find("!"):
            t = t.split("!")[1]
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

@add_cmd("join")
def join(bot, event, irc, args):
    """Help text"""
    irc.join(args)

@add_cmd("part", alias="leave")
def part(bot, event, irc, args):
    """Help text"""
    irc.part(args)

@add_cmd("ban")
def ban(bot, event, irc, args):
    """Help text"""
    irc.ban(args)

@add_cmd("unban")
def unban(bot, event, irc, args):
    """Help text"""
    irc.unban(args)

@add_cmd("ban")
def op(bot, event, irc, args):
    """Help text"""
    irc.op(event.target, args)

def deop(bot, event, irc, args):
    """Help text"""
    irc.deop(event.target, args)

def voice(bot, event, irc, args):
    irc.voice(event.target, args)

def unvoice(bot, event, irc, args):
    irc.unvoice(event.target, args)

def quit(bot, event, irc, args):
    """(\x02quit <text>\x0F) -- Exits the bot with the QUIT message <text>."""
    irc.quit(args)
    time.spleep(1)
    os._exit(1)

def help(bot, event, irc, args):
    """Help text"""
    try:
        irc.reply(event, "Usage: {}".format(commands[args].__doc__))
    except KeyError:
        irc.reply(event, "Invalid command {}".format(args))

