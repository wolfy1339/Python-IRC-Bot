import re

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def set_mode(irc, channel, users, mode):
    for block in chunks(users, 4):
        modes = "".join(mode[1:]) * len(block)
        irc.mode(channel, " ".join(block), mode[0] + modes)


def get_users(args):
    if args.find(",") != -1:
        pos = args.rfind(",")
        users_str = args[:pos].strip()
        if args[pos + 1] != " ":
            users = users_str.split(",")
        else:
            users = users_str.split(", ")
        pos += 1
        args = args[pos:].strip().split(" ")

        users.append(args[0])
    else:
        args_list = args.split(" ")
        if len(args_list) == 1:
            users = args_list[0]
        elif len(args_list) >= 2:
            users = args_list[:-1]

    return users


def get_user_host(userdb, channel, nick):
    return userdb.get_user_host(channel, nick)


def get_info_tuple(event, args, userdb=None):
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
    if not " ".join(args[:-len(users)]) == '':
        message = " ".join(args[:-len(users)])
    else:
        message = "{0}".format(event.source.nick)
    for (i, v) in enumerate(users):
        if not v.find("!") != -1 and userdb is not None:
            users[i] = get_user_host(userdb, event.target, v)
    return channel, users, message
