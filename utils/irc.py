import time
from typing import List, Optional
from utils import tasks

from zirc.event import Event
from utils.database import Database

from zirc.wrappers import connection_wrapper


def chunks(l: List, n: int):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def set_mode(irc: connection_wrapper, channel: str, users: List[str], mode: str):
    for block in chunks(users, 4):
        modes = "".join(mode[1:]) * len(block)
        irc.mode(channel, " ".join(block), mode[0] + modes)


def get_users(args: str):
    if args.find(",") != -1:
        pos = args.find(",")
        users_str = args[pos:].strip()
        if args[pos + 1] != " ":
            users = users_str[1:].split(",")
        else:
            users = users_str[2:].split(", ")
        args = args[:pos].strip().split(" ")

        users.append(args[-1])
    else:
        args_list = args.split(" ")
        if len(args_list) == 1:
            users = args_list[0]
        elif len(args_list) >= 2:
            users = args_list[:-1]

    return users


def get_user_host(userdb: Database, channel: str, nick: str):
    return userdb.get_user_host(channel, nick)


def get_info_tuple(event: Event, args: List[str], userdb: Optional[Database]=None):
    if args[0].startswith("#"):
        channel = args[0]
        str_args = " ".join(args[1:])
        del args[0]
    else:
        channel = event.target
        str_args = " ".join(args)
    if str_args.find(",") != -1:
        users = get_users(str_args)
    else:
        users = args[-1:]
    if " ".join(args[:-len(users)]) != '':
        message = " ".join(args[:-len(users)])
    else:
        message = f"{event.source.nick}"
    for (i, v) in enumerate(users):
        if not v.find("!") != -1 and userdb is not None:
            users[i] = get_user_host(userdb, event.target, v)
    return channel, users, message


def unban_after_duration(irc: connection_wrapper, users: List[str], chan: str, duration: int):
    duration += int(time.time())

    def func(irc: connection_wrapper, users: List[str], chan: str):
        for i in users:
            irc.unban(chan, i)

    tasks.run_at(duration, func, (irc, users, chan))


def strip_colours(s: str):
    import re
    ccodes = ['\x0f', '\x16', '\x1d', '\x1f', '\x02',
              '\x03([1-9][0-6]?)?,?([1-9][0-6]?)?']
    for cc in ccodes:
        s = re.sub(cc, '', s)
    return s
