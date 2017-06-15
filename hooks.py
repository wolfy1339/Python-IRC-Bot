import re
from utils.util import add_hook
import log


def _replace(match, msg):
    data = match.string.split('/')
    if len(data) == 4:
        data = data[1:]
    output = msg.replace(data[1], data[2])
    return msg[0:min(len(output), 4096)]


@add_hook
def self_correct(bot, event, irc, args):
    nick = event.source.nick
    channel = event.target
    msg = bot.userdb[channel][nick]['seen'][1]
    match = re.match(r"^s[/].*[/].*$", " ".join(args))
    if match is not None:
        output = _replace(match, msg)
        irc.reply(event, '<{0}> {1}'.format(nick, output))
        log.info('Changing %s to %s', args, output)
    else:
        pass


@add_hook
def user_correct(bot, event, irc, args):
    match = re.match(r"^u[/]([\w]+)[/].*[/].*$", " ".join(args))
    if match is not None:
        nick = match.group(1)
        channel = event.target
        msg = bot.userdb[channel][nick]['seen'][1]
        output = _replace(match, msg)
        irc.reply(event, '<{0}> {1}'.format(nick, output))
        log.info('Changing %s to %s', args, output)
    else:
        pass
