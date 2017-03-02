import time
import os

from zirc.util import repl

import config
import log
from utils.util import add_cmd
import utils


@add_cmd("calc", alias=["math"], min_args=1)
def calc(bot, event, irc, args):
    """Command to do some math calculation using the math.js web API"""
    arguments = "".join(args)
    payload = {
        'expr': arguments,
        'precision': 10
    }
    r = utils.util.post("http://api.mathjs.org/v1/", json=payload)
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


@add_cmd("eval", alias=['py', '>>'], min_args=1, owner=True, hide=True)
def Eval(bot, event, irc, args):
    """Admin console"""
    console = repl.Repl({'self': bot, 'bot': bot, 'irc': irc, 'event': event})
    try:
        irc.reply(event, console.run(" ".join(args)))
    except Exception as e:
        irc.reply(event, "{0}: {1}".format(e.__class__.__name__, e.args[0]))
        utils.util.print_error(irc, event)


@add_cmd("echo", min_args=1)
def echo(bot, event, irc, args):
    """Responds with given text"""
    irc.reply(event, '\u200b' + ' '.join(args))


@add_cmd("rainbow", min_args=1)
def rainbow(bot, event, irc, args):
    """Responds with given text colored in rainbow"""
    irc.reply(event, ' '.join(args), rainbow=True)


@add_cmd("ping", min_args=0)
def ping(bot, event, irc, args):
    """Responds with pong"""
    irc.reply(event, "PONG!")


@add_cmd("join", admin=True, min_args=1)
def join(bot, event, irc, args):
    """Joins given channel"""
    irc.join(args[0], key=args[1] if len(args) >= 2 else None)


@add_cmd("part", alias=["leave"], admin=True, min_args=0)
def part(bot, event, irc, args):
    """Parts the given or the current channel"""
    if len(args):
        irc.part(args[0])
    else:
        irc.part(event.target)


@add_cmd("cycle", alias=["rejoin"], admin=True, min_args=0)
def cycle(bot, event, irc, args):
    """Parts then joins the given or the current channel"""
    if len(args):
        irc.part(args[0])
        irc.join(args[0])
    else:
        irc.part(event.target)
        irc.join(event.target)


@add_cmd("ban", admin=True, min_args=1)
def ban(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Bans a user"""
    if len(args) > 1:
        channel, users = utils.irc.get_info_tuple(event, args)[:-1]
        utils.irc.set_mode(irc, channel, users, "+b")
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


@add_cmd("kban", admin=True, min_args=1)
def kban(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Kick-bans a user
    """
    channel, users, message = utils.irc.get_info_tuple(event, args)
    utils.irc.set_mode(irc, channel, users, "+b")
    for i in users:
        irc.kick(channel, i, message)


@add_cmd("kick", admin=True, min_args=1)
def kick(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Kicks a user
    """
    channel, users, message = utils.irc.get_info_tuple(event, args)

    for i in users:
        irc.kick(channel, i, message)


@add_cmd("remove", alias=['ninja'], admin=True, min_args=1)
def remove(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Forces a user to part the channel.
    """
    channel, users, message = utils.irc.get_info_tuple(event, args)
    if message == event.source.nick:
        message = "{0} says GTFO!".format(event.source.nick)
    for i in users:
        irc.remove(channel, i, message)


@add_cmd("unban", admin=True, min_args=1)
def unban(bot, event, irc, args):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Unbans a user"""
    channel, users = utils.irc.get_info_tuple(event, args)[:-1]
    utils.irc.set_mode(irc, channel, users, "-b")


@add_cmd("op", admin=True, min_args=0)
def op(bot, event, irc, args):
    """[<channel>] <nick>[, <nick>, ...]
    Give operator status to a user"""
    if len(args):
        channel, users = utils.irc.get_info_tuple(event, args)[:-1]
        utils.irc.set_mode(irc, channel, users, "+o")
    else:
        irc.op(event.target, event.source.nick)


@add_cmd("deop", admin=True, min_args=0)
def deop(bot, event, irc, args):
    """[<channel>] <nick>[, <nick>, ...]
    Remove operator status from a user"""
    if len(args):
        channel, users = utils.irc.get_info_tuple(event, args)[:-1]
        utils.irc.set_mode(irc, channel, users, "-o")
    else:
        irc.deop(event.target, event.source.nick)


@add_cmd("voice", admin=True, min_args=0)
def voice(bot, event, irc, args):
    """[<channel>] <nick>[, <nick>, ...]
    Give voiced status a user"""
    if len(args):
        channel, users = utils.irc.get_info_tuple(event, args)[:-1]
        utils.irc.set_mode(irc, channel, users, "+v")
    else:
        irc.voice(event.target, event.source.nick)


@add_cmd("unvoice", admin=True, min_args=0)
def unvoice(bot, event, irc, args):
    """[<channel>] <nick>[, <nick>, ...]
    Remove voiced status a user"""
    if len(args):
        channel, users = utils.irc.get_info_tuple(event, args)[:-1]
        utils.irc.set_mode(irc, channel, users, "-v")
    else:
        irc.unvoice(event.target, event.source.nick)


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


@add_cmd("help", min_args=0)
def Help(bot, event, irc, args):
    """Help text"""
    if len(args) >= 1:
        try:
            doc = utils.util.commands[args[0]]['func'].__doc__
            irc.reply(event, utils.irc.format_cmd_docs(doc, args[0]))
        except KeyError:
            irc.reply(event, "Invalid command {0}".format(args[0]))
    else:
        doc = utils.util.commands["help"]['func'].__doc__
        irc.reply(event, utils.irc.format_cmd_docs(doc, 'help'))


@add_cmd("list", min_args=0, alias=["ls"])
def List(bot, event, irc, args):
    """Help text"""
    if len(args) and args[0] == "alias":
        irc.reply(event, ", ".join(utils.util.alias_list))
    else:
        host = event.source.host
        channel = event.target
        is_owner = utils.util.check_perms(host, channel, owner=True)
        is_admin = utils.util.check_perms(host, channel, admin=True)
        is_trusted = utils.util.check_perms(host, channel, trusted=True)
        owner, admin, trusted, users = [], [], [], []
        text = "Commands({0!s}): {1!s}"
        for i in utils.cmd_list:
            if utils.commands[i]['perms'][2]:
                owner.append(i)
            elif utils.util.commands[i]['perms'][1]:
                admin.append(i)
            elif utils.util.commands[i]['perms'][0]:
                trusted.append(i)
            else:
                users.append(i)
        if is_owner:
            cmd_list = owner + admin + trusted + users
            irc.reply(event, text.format('Owner', ", ".join(cmd_list)))
        elif is_admin:
            cmd_list = admin + trusted + users
            irc.reply(event, text.format('Admin', ", ".join(cmd_list)))
        elif is_trusted:
            cmd_list = trusted + users
            irc.reply(event, text.format('Trusted', ", ".join(cmd_list)))
        else:
            irc.reply(event, text.format('User', ", ".join(users)))


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


@add_cmd("host", min_args=0)
def hostmask(bot, event, irc, args):
    """Replies with your host"""
    irc.reply(event, event.source.host)


@add_cmd("perms", min_args=0)
def permissions(bot, event, irc, args):
    """Replies with your permission level"""
    channel = event.target
    host = event.source.host

    is_bot = host.find("/bot/") != -1
    is_bot_chan = channel in config.bots['channels']
    if utils.util.check_perms(host, channel, owner=True):
        perms = 'Owner'
    elif utils.util.check_perms(host, channel, admin=True):
        perms = 'Admin'
    elif utils.util.check_perms(host, channel, trusted=True):
        perms = 'Trusted'
    elif host in config.bots['hosts'] or (is_bot_chan and is_bot):
        perms = 'Bot'
    else:
        perms = 'User'

    irc.reply(event, perms)


@add_cmd("version", min_args=0)
def version(bot, event, irc, args):
    irc.reply(event, utils.version)


@add_cmd("flushq", alias=['flush'], min_args=0, admin=True)
def flush(bot, event, irc, args):
    bot.fp.irc_queue = []
    irc.reply(event, "Cleared IRC queue")
