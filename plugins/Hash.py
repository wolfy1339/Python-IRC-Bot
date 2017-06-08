import hashlib
from utils.util import add_cmd

@add_cmd("md5", min_args=1)
def md5(bot, irc, event, args):
    return hashlib.md5(" ".join(args).encode()).hexdigest()


@add_cmd("sha1", min_args=1)
def sha1(bot, event, irc, args):
    return hashlib.sha1(" ".join(args).encode()).hexdigest()


@add_cmd("sha256", min_args=1)
def sha256(bot, event, irc, args):
    return hashlib.sha256(" ".join(args).encode()).hexdigest()


@add_cmd("sha384", min_args=1)
def sha384(bot, event, irc, args):
    return hashlib.sha384(" ".join(args).encode()).hexdigest()


@add_cmd("sha512", min_args=1)
def sha512(bot, event, irc, args):
    return hashlib.sha512(" ".join(args).encode()).hexdigest()


@add_cmd("hash", min_args=2)
def hash_cmd(bot, irc, event, args):
    """<hashing mechanism> <string to hash>
    Return a hexadecimal digest of the hashed provided string"""
    if args[0] in hashlib.algorithms_available:
        func = getattr(hashlib, args[0])
        irc.reply(event, func(bytes(" ".join(args[1:]))).hexdigest())
    else:
        irc.reply(event, "Unknown hashing mechanism: " + args[0])
