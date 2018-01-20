import re
from utils.util import add_hook
import log
import utils


@add_hook
def self_correct(bot, event, irc, args):
    match = re.match(r"^s[/](.*)[/](.*)[/]?$", " ".join(args))
    if match is not None:
        nick = event.source.nick
        channel = event.target
        for i in bot.userdb[channel][nick]['seen']:
            msg = i['message']
            output = msg.replace(match.group(1), match.group(2))
            if msg == output:
                pass
            else:
                break
        irc.reply(event, '<{0}> {1}'.format(nick, output))
        log.info('Changing %s to %s', msg, output)
    else:
        pass


@add_hook
def user_correct(bot, event, irc, args):
    match = re.match(r"^u[/]([\w]+)[/](.*)[/](.*)[/]?$", " ".join(args))
    if match is not None:
        nick = match.group(1)
        channel = event.target
        for i in bot.userdb[channel][nick]['seen']:
            msg = i['message']
            output = msg.replace(match.group(2), match.group(3))
            if msg == output:
                pass
            else:
                break
        irc.reply(event, '<{0}> {1}'.format(nick, output))
        log.info('Changing %s to %s', args, output)
    else:
        pass

@add_hook
def titler(bot, event, irc, args):
    match = re.match(r"(?:http://|https://)([^\s]+)", " ".join(args))
    if match is not None:
        r = utils.util.get(match.string)
        t = re.search(r"<title>(.*)</title>", r.text)
        url = match.group(1).split("/")[0]
        irc.reply(event, "[{0!s}] - {1!s}".format(t, url))
