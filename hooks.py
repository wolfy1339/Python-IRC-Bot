from contextlib import closing
from bs4 import BeautifulSoup
import re
from utils.util import add_hook, print_error
import requests
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

def _get_title(url):
    with closing(utils.util.get(url, stream=True, timeout=3)) as r:
        status = r.status_code
        headers = r.headers
        data = r.raw.read(16384, True).decode('UTF-8', 'replace')
    soup = BeautifulSoup(data, 'html.parser')
    try:
        t = soup.title.string
        title = re.sub(r'[\t\r\n]', ' ', t)
        # Remove ASCII control characters
        title = re.sub(r'[\x00-\x1E]', '', title)
        title = title.strip()
        if len(title) > 300:
            title = '{0}... (truncated)'.format(title[:300])
    except (AttributeError, TypeError):
        if headers.get('content-type'):
            title = ('${ORANGE}{0}${NOARMAL} '
                     '${GREEN}{1}${NORMAL}'.format(status,
                                            headers['content-type']))
        else:
            title = '${ORNAGE}{0}${NORMAL} ${RED}[no title]${NOARMAL}'.format(status)
    return title

@add_hook
def titler(bot, event, irc, args):
    # Implementation taken from Eleos
    match = re.match(r"(?:http://|https://)([^\s]+)", " ".join(args))
    if match is not None:
        try:
            url = match.group(1).split("/")[0]
            title = "[{0!s}] - {1!s}".format(_get_title(match.string), url)
        except requests.Timeout:
            title = '${RED}[timeout]${NORMAL}'
        except requests.TooManyRedirects:
            title = '${RED}[too many redirects]${NORMAL}'
        except Exception:
            title = '${RED}[error]\x0F'
            print_error(irc, event)
        irc.reply(event, title)
