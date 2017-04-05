import random
import time

import config
import logging


def check_ignored(host, channel):
    ignores = config.ignores['global']
    try:
        ignores.extend(config.ignores['channel'][channel])
    except KeyError:
        pass

    for i in ignores:
        ihost = i[0]
        expires = i[1]
        # if duration is not None, check if it's in the past, else say True
        is_past = time.time() > expires if expires is not None else True
        if host == ihost and is_past:
            return True
        elif ihost == host and not is_past:
            del config.ignores['channel'][channel][host]
            break

    return False


def add_ignore(irc, event, args):
    host = args[0]
    base_message = "Ignoring %s for %s seconds"
    indefinite = "Ignoring %s indefinately"
    if len(args) > 1:
        if args[1] == 'random':
            duration = random.randrange(100, 10000)
            expires = duration + int(time.time())
        else:
            duration = int(args[1])
            expires = duration + int(time.time())
    else:
        expires = None
    channel = args[2] if len(args) > 2 else None

    if channel is not None:
        try:
            i = config.ignores['channels'][channel]
        except KeyError:
            i = config.ignores['channels'][channel] = []
        i.append([host, expires])
    else:
        i = config.ignores['global']
        i.append([host, expires])
    if expires is not None:
        if channel is not None:
            logging.info(base_message + " in %s", host, duration, channel)
        else:
            logging.info(base_message, host, duration)
    else:
        if channel is not None:
            logging.info(indefinite + " in %s", host, channel)
        else:
            logging.info(indefinite, host)