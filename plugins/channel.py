from typing import List, TYPE_CHECKING
import utils
from utils.util import add_cmd

if TYPE_CHECKING:
    from zirc.wrappers import connection_wrapper
    from bot import Bot
    from zirc.event import Event


@add_cmd("join", trusted=True, min_args=1)
def join(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """<channel>
    Joins given channel"""
    irc.join(args[0], key=args[1] if len(args) >= 2 else None)


@add_cmd("part", alias=["leave"], trusted=True, min_args=0)
def part(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """[<channel>]
    Parts the given or the current channel"""
    if len(args):
        irc.part(args[0])
    else:
        irc.part(event.target)


@add_cmd("cycle", alias=["rejoin"], admin=True, min_args=0)
def cycle(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """[<channel>]
    Parts then joins the given or the current channel"""
    if len(args):
        irc.part(args[0])
        irc.join(args[0])
    else:
        irc.part(event.target)
        irc.join(event.target)


@add_cmd("ban", admin=True, min_args=1)
def ban(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Bans a user"""
    if len(args) > 2 or " ".join(args).find(",") != -1:
        channel, users = utils.irc.get_info_tuple(event, args, bot.userdb)[:-1]
        utils.irc.set_mode(irc, channel, users, "+b")
    else:
        if args[0].find('@') != -1:
            host = args[0]
        else:
            try:
                host = f"*!*@{bot.userdb[event.target][args[0]]['host']}"
            except KeyError:
                irc.send(f"WHO {event.target} nuhs%nhuac")
                host = f"*!*@{bot.userdb[event.target][args[0]]['host']}"
        irc.ban(event.target, host)


@add_cmd("kban", admin=True, min_args=1)
def kban(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Kick-bans a user
    """
    channel, users, message = utils.irc.get_info_tuple(event, args, bot.userdb)
    utils.irc.set_mode(irc, channel, users, "+b")
    for i in utils.irc.get_users(" ".join(args)):
        irc.kick(channel, i, message)


@add_cmd("kick", admin=True, min_args=1)
def kick(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Kicks a user
    """
    channel, users, message = utils.irc.get_info_tuple(event, args)

    for i in users:
        irc.kick(channel, i, message)


@add_cmd("remove", alias=['ninja'], admin=True, min_args=1)
def remove(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Forces a user to part the channel.
    """
    channel, users, message = utils.irc.get_info_tuple(event, args)
    if message == event.source.nick:
        message = f"{event.source.nick} says GTFO!"
    for i in users:
        irc.remove(channel, i, message)


@add_cmd("unban", admin=True, min_args=1)
def unban(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """[<channel>] [<message>] <nick>[, <nick>, ...]
    Unbans a user"""
    channel, users = utils.irc.get_info_tuple(event, args, bot.userdb)[:-1]
    utils.irc.set_mode(irc, channel, users, "-b")


@add_cmd("op", admin=True, min_args=0)
def op(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """[<channel>] <nick>[, <nick>, ...]
    Give operator status to a user"""
    if len(args):
        channel, users = utils.irc.get_info_tuple(event, args)[:-1]
        utils.irc.set_mode(irc, channel, users, "+o")
    else:
        irc.op(event.target, event.source.nick)


@add_cmd("deop", admin=True, min_args=0)
def deop(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """[<channel>] <nick>[, <nick>, ...]
    Remove operator status from a user"""
    if len(args):
        channel, users = utils.irc.get_info_tuple(event, args)[:-1]
        utils.irc.set_mode(irc, channel, users, "-o")
    else:
        irc.deop(event.target, event.source.nick)


@add_cmd("voice", admin=True, min_args=0)
def voice(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """[<channel>] <nick>[, <nick>, ...]
    Give voiced status a user"""
    if len(args):
        channel, users = utils.irc.get_info_tuple(event, args)[:-1]
        utils.irc.set_mode(irc, channel, users, "+v")
    else:
        irc.voice(event.target, event.source.nick)


@add_cmd("unvoice", admin=True, min_args=0)
def unvoice(bot: Bot, event: Event, irc: connection_wrapper, args: List[str]):
    """[<channel>] <nick>[, <nick>, ...]
    Remove voiced status a user"""
    if len(args):
        channel, users = utils.irc.get_info_tuple(event, args)[:-1]
        utils.irc.set_mode(irc, channel, users, "-v")
    else:
        irc.unvoice(event.target, event.source.nick)
