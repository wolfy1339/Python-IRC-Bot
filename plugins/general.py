from __future__ import annotations
import time
from typing import List, TYPE_CHECKING
import config
import utils
from utils.util import add_cmd

if TYPE_CHECKING:
    from utils.database import SeenDB
    from zirc.event import Event
    from zirc.wrappers import connection_wrapper
    from bot import Bot


@add_cmd("shrug", min_args=0)
def shrug(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """Sends a shrug to the channel"""
    irc.reply(event, "\u00AF\\_(\u30C4)_/\u00AF")


@add_cmd("calc", alias=["math"], min_args=1)
def calc(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
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
        message = f"The answer is: {output}"
    else:
        message = r.json()['error']
    irc.reply(event, message)


@add_cmd("echo", min_args=1)
def echo(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """Responds with given text"""
    irc.reply(event, f"\u200b{' '.join(args)}")


@add_cmd("rainbow", min_args=1)
def rainbow(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """Responds with given text colored in rainbow"""
    irc.reply(event, ' '.join(args), rainbow=True)


@add_cmd("ping", min_args=0)
def ping(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """Responds with pong"""
    irc.reply(event, "PONG!")


@add_cmd("help", min_args=0)
def help_cmd(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """<command>
    Returns help text for the specified command"""
    if len(args):
        try:
            doc = utils.util.commands[args[0]]['func'].__doc__
            irc.reply(event, utils.commands.format_cmd_docs(doc, args[0]))
        except KeyError:
            irc.reply(event, "Invalid command {0}".format(args[0]))
    else:
        doc = utils.util.commands["help"]['func'].__doc__
        irc.reply(event, utils.commands.format_cmd_docs(doc, 'help'))


@add_cmd("list", min_args=0, alias=["ls"])
def list_cmds(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
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
        if utils.util.check_perms(event, channel, owner=True):
            cmd_list += owner + admin + trusted
            msg = text.format('Owner', ", ".join(sorted(cmd_list)))
        elif utils.util.check_perms(event, channel, admin=True):
            cmd_list += admin + trusted
            msg = text.format('Admin', ", ".join(sorted(cmd_list)))
        elif utils.util.check_perms(event, channel, trusted=True):
            cmd_list += trusted
            msg = text.format('Trusted', ", ".join(sorted(cmd_list)))
        else:
            msg = text.format('User', ", ".join(sorted(cmd_list)))
        irc.reply(event, msg)


@add_cmd("perms", min_args=0)
def permissions(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """Replies with your permission level"""
    channel = event.target
    host = event.source.host

    is_bot = host.find("/bot/") != -1
    is_bot_chan = channel in config.bots['channels']
    if utils.util.check_perms(event, channel, owner=True):
        perms = 'Owner'
    elif utils.util.check_perms(event, channel, admin=True):
        perms = 'Admin'
    elif utils.util.check_perms(event, channel, trusted=True):
        perms = 'Trusted'
    elif host in config.bots['hosts'] or (is_bot_chan and is_bot):
        perms = 'Bot'
    else:
        perms = 'User'

    irc.reply(event, perms)


@add_cmd("version", min_args=0)
def version(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    irc.reply(event, utils.version)


@add_cmd("host", min_args=0)
def hostmask(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """Replies with your host"""
    irc.reply(event, event.source.host)


@add_cmd("seen", min_args=1)
def seen(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
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
    msg = [f"I have last seen {nick} "]
    try:
        db = sorted(bot.userdb[channel][nick]["seen"], key=lambda x: x['time'], reverse=True)
        elapsed = int(time.time() - db[0]["time"])
        day = 24 * 60 * 60
        year, elapsed = elapsed // (365 * day), elapsed % (365 * day)
        if year > 0:
            msg.append(f"{year} years, ")
        weeks, elapsed = elapsed // (7 * day), elapsed % (7 * day)
        if weeks > 0:
            msg.append(f"{weeks} weeks, ")
        days, elapsed = elapsed // day, elapsed % day
        if days > 0:
            msg.append(f"{days} days, ")
        hours, elapsed = elapsed // (60 * 60), elapsed % (60 * 60)
        if hours > 0:
            msg.append(f"{hours} hours, ")
        minutes, seconds = elapsed // (60), elapsed % (60)
        if minutes > 0:
            msg.append(f"{minutes} minutes, ")
        msg.append(f"{seconds} seconds")
        msg.append(f"ago: {db[0]['message']}")

        irc.reply(event, " ".join(msg))
    except (KeyError, TypeError):
        irc.reply(event, f"I have not seen {nick}")
