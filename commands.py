import math
import time
import os
import re
import log
from utils import add_cmd
import utils
import config


def normalizeWhitespace(s, removeNewline=True):
    """Normalizes the whitespace in a string; \s+ becomes one space."""
    if not s:
        return str(s)  # not the same reference
    starts_with_space = (s[0] in ' \n\t\r')
    ends_with_space = (s[-1] in ' \n\t\r')
    if removeNewline:
        newline_re = re.compile('[\r\n]+')
        s = ' '.join(filter(bool, newline_re.split(s)))
    s = ' '.join(filter(bool, s.split('\t')))
    s = ' '.join(filter(bool, s.split(' ')))
    if starts_with_space:
        s = ' ' + s
    if ends_with_space:
        s += ' '
    return s


def formatCmdDocs(docs, name):
    doclines = docs.splitlines()
    s = '%s %s' % (name, doclines.pop(0))
    if doclines:
        doc = ' '.join(doclines)
        s = '(%s) -- %s' % ('\x02' + s + '\x0F', doc)
    return normalizeWhitespace(s)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]


def setMode(event, irc, args, mode):
    if args[0].find("#") != -1:
        for block in chunks(args[1:], 4):
            modes = "".join(mode[1:]) * len(block)
            irc.mode(args[0], " ".join(block), "".join(mode[:1]) + modes)
    else:
        for block in chunks(args, 4):
            modes = "".join(mode[1:]) * len(block)
            irc.mode(event.target, " ".join(block), "".join(mode[:1]) + modes)


def getUsersFromCommaList(args):
    pos = args.rfind(",")
    if args[pos + 1] != " ":
        users = args[:pos].strip().split(",")
    else:
        users = args[:pos].strip().split(", ")
    args = args[pos:].strip().split(" ")

    users.append(args[0][1:])
    return users


def x(event, args):
    if args[0].startswith("#"):
        channel = args[0]
        str_args = " ".join(args[1:])
        if str_args.find(",") != -1:
            users = getUsersFromCommaList(str_args)
        else:
            users = args[-1:]
        if not " ".join(args[:-len(users)]) == '':
            message = " ".join(args[:-len(users)])
        else:
            message = "{0}".format(event.source.nick)
    else:
        channel = event.target
        str_args = " ".join(args)
        if str_args.find(",") != -1:
            users = getUsersFromCommaList(str_args)
        else:
            users = args[-1:]
        if not " ".join(args[:-len(users)]) == '':
            message = " ".join(args[:-len(users)])
        else:
            message = "{0}".format(event.source.nick)
    return channel, users, message


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
    try:
        irc.reply(event, repr(eval(" ".join(args))))
    except Exception as e:
        irc.reply(event, "{0}: {1}".format(e.__class__.__name__, e.args[0]))
        utils.PrintError(irc, event)


@add_cmd("echo", minArgs=1)
def echo(bot, event, irc, args):
    """Responds with given text"""
    irc.reply(event, ' '.join(args))


@add_cmd("rainbow", minArgs=1)
def rainbow(bot, event, irc, args):
    """Responds with given text colored in rainbow"""
    irc.reply(event, ' '.join(args), color="rainbow")


@add_cmd("ping", minArgs=0)
def ping(bot, event, irc, args):
    """Help text"""
    irc.reply(event, "PONG!")


@add_cmd("join", admin=True, minArgs=1)
def join(bot, event, irc, args):
    """Joins given channel"""
    irc.join(args[0], key=args[1] if len(args) >= 2 else None)


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


@add_cmd("kban", admin=True, minArgs=1)
def kban(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Kick-bans a user
    """
    if len(args) > 1:
        setMode(event, irc, args, "+b")

        channel, users, message = x(event, args)
        for i in users:
            try:
                irc.ban(channel, "*!*@" + bot.userdb[i]['host'])
            except KeyError:
                irc.send("WHO {0} nuhs%nhua".format(event.target))
                irc.ban(channel, "*!*@" + bot.userdb[i]['host'])
            irc.kick(channel, i, message)
    else:
        irc.ban(event.target, args[0])
        irc.kick(event.target, args[0], " ".join(args[1:]))


@add_cmd("kick", admin=True, minArgs=1)
def kick(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Kicks a user
    """
    if len(args) > 1:
        channel, users, message = x(event, args)

        for i in users:
            irc.kick(channel, i, message)
    else:
        irc.kick(event.target, args[0], " ".join(args[1:]))


@add_cmd("remove", alias=['ninja'], admin=True, minArgs=1)
def remove(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Forces a user to part the channel.
    """
    if len(args) > 1:
        channel, users, message = x(event, args)
        if message == event.source.nick:
            message = "{0} says GTFO!".format(event.source.nick)
        for i in users:
            irc.remove(channel, i, message)
    else:
        irc.remove(event.target, args[0], " ".join(args[1:]))


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
            if args[0] == 'password' and event.target.startswith('#'):
                irc.reply(event, "Are you sure you want this to be diplayed in a public channel?")
            else:
                irc.reply(event, repr(getattr(config, args[0])))
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
            irc.reply(event, formatCmdDocs(doc, args[0]))
        except KeyError:
            irc.reply(event, "Invalid command {0}".format(args[0]))
    else:
        doc = utils.commands["help"]['func'].__doc__
        irc.reply(event, formatCmdDocs(doc, 'help'))


@add_cmd("list", minArgs=0, alias=["ls"])
def List(bot, event, irc, args):
    """Help text"""
    if len(args) and args[0] == "alias":
        irc.reply(event, ", ".join(utils.alias_list))
    else:
        irc.reply(event, ", ".join(utils.cmd_list))


@add_cmd("reload", admin=True, minArgs=1, hide=True)
def Reload(bot, event, irc, args):
    """Help text"""
    global reload
    if utils.PY34:
        reload = __import__("importlib").reload
    elif utils.PY3:
        reload = __import__("imp").reload

    if args[0] in ['commands', 'utils', 'config']:
        try:
            reload(__import__(args[0]))
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
    isBot = host.find("/bot/") != -1
    isBotChannel = event.target in config.bots['channels']

    if host in config.owners:
        perms = 'Owner'
    elif host in config.admins:
        perms = 'Admin'
    elif host in config.trusted:
        perms = 'Trusted'
    elif host in config.bots['hosts'] or (isBotChannel and isBot):
        perms = 'Bot'
    else:
        perms = 'User'

    irc.reply(event, perms)


@add_cmd("version", minArgs=0)
def version(bot, event, irc, args):
    sysver = "".join(__import__("sys").version.split("\n"))
    botver = "A zIRC bot v{0}, running on Python {1}".format("0.1", sysver)
    irc.reply(event, botver)


@add_cmd("flushq", alias=['flush'], minArgs=0, admin=True)
def flush(bot, event, irc, args):
    bot.fp.irc_queue = []
    irc.reply(event, "Cleared IRC queue")
