import re
from utils.util import add_hook
import log
import utils


def _replace(match, msg):
    data = match.string.split('/')
    if len(data) == 4:
        data = data[1:]
    output = msg.replace(data[1], data[2])
    return output[0:min(len(output), 4096)]


@add_hook
def self_correct(bot, event, irc, args):
    match = re.match(r"^s[/].*[/].*$", " ".join(args))
    if match is not None:
        nick = event.source.nick
        channel = event.target
        for i in bot.userdb[channel][nick]['seen']
            msg = i['messsage']
            output = _replace(match, msg)
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

@add_hook
def titler(bot, event, irc, args):
    match = re.match(r"(?:http://|https://)([^\s]+)", " ".join(args))
    if match is not None and event.target != "##lazy-valoran":
        r = utils.util.get(match.string)
        t = re.search(r"<title>(.*)</title>", r.text)
        url = match.group(1).split("/")[0]
        irc.reply(event, "[{0!s}] - {1!s}".format(t, url))
