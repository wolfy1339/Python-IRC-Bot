import random
import time
from typing import List
from zirc.event import Event

from zirc.wrappers import connection_wrapper

import config
import log as logging


def check_ignored(host: str, channel: str):
    ignores = config.ignores['global']
    if channel in config.ignores['channels'].keys():
        # ignores = {'channels': {'##lazy-valoran':[[uhost, expires]]}}
        ignores.extend(config.ignores['channels'][channel])

    for i in ignores:
        for (uhost, expires) in i:
            # if duration is not None, check if it's in the past, else say True
            is_past = time.time() > expires if expires is not None else True
            if host == uhost and is_past:
                return True
            elif host == uhost and not is_past:
                del config.ignores['channels'][channel][host]
                break

    return False


def add_ignore(irc: connection_wrapper, event: Event, args: List[str]):
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
            logging.info(f'{base_message} in %s', host, duration, channel)
        else:
            logging.info(base_message, host, duration)
    else:
        if channel is not None:
            logging.info(f'{indefinite} in %s', host, channel)
        else:
            logging.info(indefinite, host)
