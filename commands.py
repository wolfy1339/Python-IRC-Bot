import time
import os
import re

from zirc.util import repl

import config
import log
from utils import add_cmd
import utils


def normalizeWhitespace(s, removeNewline=True):
    """Normalizes the whitespace in a string; \s+ becomes one space."""
    if not s:
        return str(s)  # not the same reference
    starts_with_space = (s[0] in ' \n\t\r')
    ends_with_space = (s[-1] in ' \n\t\r')
    if removeNewline:
        newline_re = re.compile('[\r\n]+')
        s = ' '.join([i for i in newline_re.split(s) if bool(i)])
    s = ' '.join([i for i in s.split('\t') if bool(i)])
    s = ' '.join([i for i in s.split(' ') if bool(i)])
    if starts_with_space:
        s = ' ' + s
    if ends_with_space:
        s += ' '
    return s


def formatCmdDocs(docs, name):
    doclines = docs.splitlines()
    s = '{0!s} {1!s}'.format(name, doclines.pop(0))
    if doclines:
        doc = ' '.join(doclines)
        s = '({0!s}) -- {1!s}'.format('\x02' + s + '\x0F', doc)
    return normalizeWhitespace(s)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]


def setMode(irc, channel, users, mode):
    for block in chunks(users, 4):
        modes = "".join(mode[1:]) * len(block)
        irc.mode(channel, " ".join(block), mode[0] + modes)


def getUsersFromCommaList(args):
    pos = args.rfind(",")
    if args[pos + 1] != " ":
        users = args[:pos].strip().split(",")
    else:
        users = args[:pos].strip().split(", ")
    args = args[pos:].strip().split(" ")

    users.append(args[0][1:])
    return users


def getInfoTuple(event, args):
    if args[0].startswith("#"):
        channel = args[0]
        str_args = " ".join(args[1:])
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
    """Command to do some math calculation using the math.js web API"""
    arguments = "".join(args)
    payload = {
        'expr': arguments,
        'precision': 10
    }
    r = utils.post("http://api.mathjs.org/v1/", json=payload)
    if not r.json()['error']:
        result = r.json()['result']
        if not result.find('.'):
            output = format(int(result), ",d")
        else:
            output = result
        message = "The answer is: {0}".format(output)
    else:
        message = r.json()['error']
    irc.reply(event, message)


@add_cmd("eval", alias=['py', '>>'], minArgs=1, owner=True, hide=True)
def Eval(bot, event, irc, args):
    """Admin console"""
    console = repl.Repl({'self': bot, 'bot': bot, 'irc': irc, 'event': event})
    try:
        irc.reply(event, console.run(" ".join(args)))
    except Exception as e:
        irc.reply(event, "{0}: {1}".format(e.__class__.__name__, e.args[0]))
        utils.PrintError(irc, event)


@add_cmd("echo", minArgs=1)
def echo(bot, event, irc, args):
    """Responds with given text"""
    irc.reply(event, '\u200b' + ' '.join(args))


@add_cmd("rainbow", minArgs=1)
def rainbow(bot, event, irc, args):
    """Responds with given text colored in rainbow"""
    irc.reply(event, ' '.join(args), rainbow=True)


@add_cmd("ping", minArgs=0)
def ping(bot, event, irc, args):
    """Responds with pong"""
    irc.reply(event, "PONG!")


@add_cmd("join", admin=True, minArgs=1)
def join(bot, event, irc, args):
    """Joins given channel"""
    irc.join(args[0], key=args[1] if len(args) >= 2 else None)


@add_cmd("part", alias=["leave"], admin=True, minArgs=0)
def part(bot, event, irc, args):
    """Parts the given or the current channel"""
    if len(args):
        irc.part(args[0])
    else:
        irc.part(event.target)


@add_cmd("cycle", alias=["rejoin"], admin=True, minArgs=0)
def cycle(bot, event, irc, args):
    """Parts then joins the given or the current channel"""
    if len(args):
        irc.part(args[0])
        irc.join(args[0])
    else:
        irc.part(event.target)
        irc.join(event.target)


@add_cmd("ban", admin=True, minArgs=1)
def ban(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Bans a user"""
    if len(args) > 1:
        channel, users = getInfoTuple(event, args)[:-1]
        setMode(irc, channel, users, "+b")
    else:
        if args[0].find('@') == -1:
            host = args[0]
        else:
            try:
                host = "*!*@" + bot.userdb[event.target][args[0]]['host']
            except KeyError:
                irc.send("WHO {0} nuhs%nhuac".format(event.target))
                host = "*!*@" + bot.userdb[event.target][args[0]]['host']
        irc.ban(event.target, host)


@add_cmd("kban", admin=True, minArgs=1)
def kban(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Kick-bans a user
    """
    channel, users, message = getInfoTuple(event, args)
    setMode(irc, channel, users, "+b")
    for i in users:
        irc.kick(channel, i, message)

@add_cmd("kick", admin=True, minArgs=1)
def kick(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Kicks a user
    """
    channel, users, message = getInfoTuple(event, args)

    for i in users:
        irc.kick(channel, i, message)


@add_cmd("remove", alias=['ninja'], admin=True, minArgs=1)
def remove(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Forces a user to part the channel.
    """
    channel, users, message = getInfoTuple(event, args)
    if message == event.source.nick:
        message = "{0} says GTFO!".format(event.source.nick)
    for i in users:
        irc.remove(channel, i, message)


@add_cmd("unban", admin=True, minArgs=1)
def unban(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Unbans a user"""
    channel, users = getInfoTuple(event, args)[:-1]
    setMode(irc, channel, users, "-b")


@add_cmd("op", admin=True, minArgs=0)
def op(bot, event, irc, args):
    """[<channel>] <nick>[, <nick>, ...]
    Give operator status to a user"""
    if len(args):
        channel, users = getInfoTuple(event, args)[:-1]
        setMode(irc, channel, users, "+o")
    else:
        irc.op(event.target, event.source.nick)


@add_cmd("deop", admin=True, minArgs=0)
def deop(bot, event, irc, args):
    """[<channel>] <nick>[, <nick>, ...]
    Remove operator status from a user"""
    if len(args):
        channel, users = getInfoTuple(event, args)[:-1]
        setMode(irc, channel, users, "-o")
    else:
        irc.deop(event.target, event.source.nick)


@add_cmd("voice", admin=True, minArgs=0)
def voice(bot, event, irc, args):
    """[<channel>] <nick>[, <nick>, ...]
    Give voiced status a user"""
    if len(args):
        channel, users = getInfoTuple(event, args)[:-1]
        setMode(irc, channel, users, "+v")
    else:
        irc.voice(event.target, event.source.nick)


@add_cmd("unvoice", admin=True, minArgs=0)
def unvoice(bot, event, irc, args):
    """[<channel>] <nick>[, <nick>, ...]
    Remove voiced status a user"""
    if len(args):
        channel, users = getInfoTuple(event, args)[:-1]
        setMode(irc, channel, users, "-v")
    else:
        irc.unvoice(event.target, event.source.nick)


@add_cmd("nick", owner=True, minArgs=1)
def nick(bot, event, irc, args):
    """<nick>
    Changes the bot's nickname"""
    bot.config['nickname'] = args[0]
    irc.nick(args[0])


@add_cmd("log.level", admin=True, minArgs=1)
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


@add_cmd("config", admin=True, minArgs=1, alias=['cfg'])
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


@add_cmd("quit", admin=True, minArgs=0)
def Quit(bot, event, irc, args):
    """<text>
    Exits the bot with the QUIT message <text>."""
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
        host = event.source.host
        channel = event.target
        isOwner = utils.checkPerms(host, channel, owner=True)
        isAdmin = utils.checkPerms(host, channel, admin=True)
        isTrusted = utils.checkPerms(host, channel, trusted=True)
        owner, admin, trusted, users = [], [], [], []
        text = "Commands({}): "
        for i in utils.cmd_list:
            if utils.commands[i]['perms'][2]:
                owner.append(i)
            elif utils.commands[i]['perms'][1]:
                admin.append(i)
            elif utils.commands[i]['perms'][0]:
                trusted.append(i)
            else:
                users.append(i)
        if isOwner:
            cmd_list = owner + admin + trusted + users
            irc.reply(event, text.format('Owner') + ", ".join(cmd_list))
        elif isAdmin:
            cmd_list = admin + trusted + users
            irc.reply(event, text.format('Admin') + ", ".join(cmd_list))
        elif isTrusted:
            cmd_list = trusted + users
            irc.reply(event, text.format('Trusted') + ", ".join(cmd_list))
        else:
            irc.reply(event, text.format('User') + ", ".join(users))


@add_cmd("reload", admin=True, minArgs=1, hide=True)
def Reload(bot, event, irc, args):
    """Help text"""
    if utils.PY34:
        reload = __import__("importlib").reload
    elif utils.PY3:
        reload = __import__("imp").reload
    elif utils.PY2:
        reload = __builtins__.reload

    if args[0] in ['commands', 'utils', 'config', 'log']:
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
    channel = event.target
    host = event.source.host

    isBot = host.find("/bot/") != -1
    isBotChannel = channel in config.bots['channels']
    if utils.checkPerms(host, channel, owner=True):
        perms = 'Owner'
    elif utils.checkPerms(host, channel, admin=True):
        perms = 'Admin'
    elif utils.checkPerms(host, channel, trusted=True):
        perms = 'Trusted'
    elif host in config.bots['hosts'] or (isBotChannel and isBot):
        perms = 'Bot'
    else:
        perms = 'User'

    irc.reply(event, perms)


@add_cmd("version", minArgs=0)
def version(bot, event, irc, args):
    irc.reply(event, utils.version)


@add_cmd("flushq", alias=['flush'], minArgs=0, admin=True)
def flush(bot, event, irc, args):
    bot.fp.irc_queue = []
    irc.reply(event, "Cleared IRC queue")
