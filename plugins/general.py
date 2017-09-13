import math
import config
import utils
from utils.util import add_cmd


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
        if not result.find('.') != -1 or result.find("e") != -1:
            output = format(int(float(result)), ",d")
        else:
            output = result
        message = "The answer is: {0}".format(output)
    else:
        message = r.json()['error']
    irc.reply(event, message)


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


@add_cmd("help", min_args=0)
def help_cmd(bot, event, irc, args):
    """<command>
    Returns help text for the specified command"""
    if len(args) >= 1:
        try:
            doc = utils.util.commands[args[0]]['func'].__doc__
            irc.reply(event, utils.commands.format_cmd_docs(doc, args[0]))
        except KeyError:
            irc.reply(event, "Invalid command {0}".format(args[0]))
    else:
        doc = utils.util.commands["help"]['func'].__doc__
        irc.reply(event, utils.commands.format_cmd_docs(doc, 'help'))


@add_cmd("list", min_args=0, alias=["ls"])
def list_cmds(bot, event, irc, args):
    """Help text"""
    if len(args) and args[0] == "alias":
        irc.reply(event, ", ".join(utils.util.alias_list))
    else:
        host = event.source.host
        channel = event.target
        owner, admin, trusted, users = [], [], [], []
        text = "Commands({0!s}): {1!s}"
        for i in utils.util.cmd_list:
            if utils.util.commands[i]['perms'][2]:
                owner.append(i)
            elif utils.util.commands[i]['perms'][1]:
                admin.append(i)
            elif utils.util.commands[i]['perms'][0]:
                trusted.append(i)
            else:
                users.append(i)
        cmd_list = users
        if utils.util.check_perms(host, channel, owner=True):
            cmd_list += owner + admin + trusted
            msg = text.format('Owner', ", ".join(sorted(cmd_list)))
        elif utils.util.check_perms(host, channel, admin=True):
            cmd_list += admin + trusted
            msg = text.format('Admin', ", ".join(sorted(cmd_list)))
        elif utils.util.check_perms(host, channel, trusted=True):
            cmd_list += trusted
            msg = text.format('Trusted', ", ".join(sorted(cmd_list)))
        else:
            msg = text.format('User', ", ".join(sorted(cmd_list)))
        irc.reply(event, msg)


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


@add_cmd("host", min_args=0)
def hostmask(bot, event, irc, args):
    """Replies with your host"""
    irc.reply(event, event.source.host)


@add_cmd("seen", min_args=1)
def seen(bot, event, irc, args):
    """[<channel>] <nick>
    Returns the last time <nick> was seen and what <nick> was last seen saying.
    <channel> is only necessary if the message isn't sent on the channel itself.
    """
    if args[0].startswith("#"):
        channel = args[0]
        nick = args[1]
    else:
        channel = event.target
        nick = args[0]
    try:
        db = bot.userdb[channel][nick]["seen"]
        seendb = sorted(db, key=lambda x: x["time"])
        ago = seendb[0]["time"]
        day = int(math.floor(ago / 86400))
        hour = int(math.floor((ago % 86400) / 3600))
        minute = int(math.floor((ago - (day * 86400) - (hour * 3600)) / 60))
        second = int(ago - (day * 86400) - (hour * 3600) - (minute * 60))
        time_ago = "{0} days {1} hours {2} months {3} seconds".format(day,
                                                                      hour,
                                                                      minute,
                                                                      second)
        last_msg = seendb[0]["message"]
        msg = "I have last seen {0} {1} ago: {2}"
        irc.reply(event, msg.format(nick, time_ago, last_msg))
    except (KeyError, TypeError):
        irc.reply(event, "I have not seen {0}".format(nick))
