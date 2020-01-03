from ast import literal_eval
import os
import time

from zirc.util import repl
import config
import log
from utils.util import add_cmd
import utils


@add_cmd("exec", min_args=1, trusted=True, hide=True)
def exec_cmd(bot, event, irc, args):
    """Executes a subprocess"""
    import subprocess
    output = ''
    try:
        output = subprocess.check_output(args, shell=True, stderr=subprocess.STDOUT)
        code = 0
    except subprocess.CalledProcessError as e:
        code = e.returncode
        output = e.output

    for line in output.decode().splitlines():
        try:
            if len(line): # Somehow this value turns out to be an integer somehow. It should never ever be one
                irc.reply(event, line)
        except Exception:
            log.error(f"Exec command error: Invalid Value: {line}")
    irc.reply(event, f"{event.source.nick}: Process's exit code is {code}")


@add_cmd("eval", alias=['py', '>>'], min_args=1, owner=True, hide=True)
def eval_cmd(bot, event, irc, args):
    """Admin console"""
    console = repl.Repl({'self': bot, 'bot': bot, 'irc': irc, 'event': event})
    try:
        output = console.run(" ".join(args)).splitlines()
        for line in output:
            if len(line):
                irc.reply(event, line)

    except Exception as e:
        irc.reply(event, f"{e.__class__.__name__}: {e.args[0]}")
        utils.util.print_error(irc, event)


@add_cmd("nick", owner=True, min_args=1)
def nick(bot, event, irc, args):
    """<nick>
    Changes the bot's nickname"""
    bot.config['nickname'] = args[0]
    irc.nick(args[0])


@add_cmd("log.level", admin=True, min_args=1)
def log_level(bot, event, irc, args):
    """<level>
    Changes the logging level"""
    try:
        log.setLevel(getattr(log, args[0].upper()))
        irc.reply(event, f"Set log level to {args[0]}")
    except AttributeError:
        irc.reply(event, f"Invalid log level {args}")


@add_cmd("config", admin=True, min_args=1, alias=['cfg'])
def config_cmd(bot, event, irc, args):
    """<nick>
    Changes or displays a config variable"""
    if len(args) > 1:
        if hasattr(config, args[0]):
            try:
                value = literal_eval(args[1])
            except Exception:
                value = args[1]
            setattr(config, args[0], value)
            irc.reply(event, f"Set config.{args[0]} to {args[1]}")
        else:
            irc.reply(event, f"Invalid config variable {args[0]}")
    else:
        if hasattr(config, args[0]):
            if args[0] == 'password' and event.target.startswith('#'):
                irc.reply(event, config.secretEntry)
            else:
                irc.reply(event, repr(getattr(config, args[0])))
        else:
            irc.reply(event, f"Invalid config variable {args[0]}")


@add_cmd("quit", admin=True, min_args=0)
def quit_cmd(bot, event, irc, args):
    """<text>
    Exits the bot with the QUIT message <text>."""
    irc.quit("zIRC - https://github.com/itslukej/zirc" if (
        not args) else " ".join(args))
    time.sleep(1)
    os._exit(0)


@add_cmd("reload", admin=True, min_args=1, hide=True)
def reload_cmd(bot, event, irc, args):
    """Help text"""
    if utils.util.PY34:
        reload = __import__("importlib").reload
    elif utils.util.PY3:
        reload = __import__("imp").reload

    if args[0] != "utils.util":
        try:
            del __import__('sys').modules[args[0]]
            reload(__import__(args[0]))
            irc.reply(event, "Reloaded {0}".format(args[0]))
        except ImportError:
            utils.util.print_error(irc, event)
    else:
        irc.reply(event, "Wrong module name")


@add_cmd("flushq", alias=['flush'], min_args=0, admin=True)
def flush(bot, event, irc, args):
    bot.fp.irc_queue = []
    irc.reply(event, "Cleared IRC queue")


@add_cmd("ignore", min_args=1, admin=True)
def add_ignore(bot, event, irc, args):
    """<host> [<duration|random>] [<channel>]
    Adds an ignore for the specified host"""
    utils.ignores.add_ignore(irc, event, args)
