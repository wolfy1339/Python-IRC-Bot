import hashlib
from utils.util import add_cmd


@add_cmd("md5", min_args=1)
def md5(bot, event, irc, args):
    irc.reply(event, hashlib.md5(" ".join(args).encode()).hexdigest())


@add_cmd("sha1", min_args=1)
def sha1(bot, event, irc, args):
    irc.reply(event, hashlib.sha1(" ".join(args).encode()).hexdigest())


@add_cmd("sha256", min_args=1)
def sha256(bot, event, irc, args):
    irc.reply(event, hashlib.sha256(" ".join(args).encode()).hexdigest())


@add_cmd("sha384", min_args=1)
def sha384(bot, event, irc, args):
    irc.reply(event, hashlib.sha384(" ".join(args).encode()).hexdigest())


@add_cmd("sha512", min_args=1)
def sha512(bot, event, irc, args):
    irc.reply(event, hashlib.sha512(" ".join(args).encode()).hexdigest())


@add_cmd("hash", min_args=2)
def hash_cmd(bot, event, irc, args):
    """<hashing mechanism> <string to hash>
    Returns a hexadecimal digest of the hashed provided string"""
    if args[0] in hashlib.algorithms_available:
        func = getattr(hashlib, args[0])
        irc.reply(event, func(" ".join(args[1:]).encode()).hexdigest())
    else:
        irc.reply(event, f"Unknown hashing mechanism: {args[0]}")
