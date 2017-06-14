import re
from utils.util import add_hook
import log


@add_hook
def user_correct(bot, event, irc, args):
    nick = event.source.nick
    channel = event.target
    msg = bot.userdb[channel][nick]['seen'][1]
    match = re.match(r"^s[/].*[/].*$", " ".join(args))
    if match is not None:
        data = match.split('/')
        output = msg.replace(data[0], data[1])
        output = msg[0:min(len(output), 4096)]

        log.info('Changing {0} to {1}'.format(args, output))
        irc.reply(event, '<{0}> {1}'.format(nick, output))
    else:
        pass
