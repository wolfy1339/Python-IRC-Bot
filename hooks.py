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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'}
    if 'google' in url or 'goo.gl' in url:
        headers['Cookie'] = "NID=127=kC6ePzilj4duAyFQnFHYFDsfLhMwM8XBb8lHNbRlMFyqpMpP9sRG9OtOihNxNVBbBiHEHFtq3zkguVYNOCoMccPk3csLpPaWevigfcUYtgsx7PUStcmAcXKWlIN-KY-m"

    with closing(requests.get(url, stream=True, timeout=4, headers=headers)) as r:
        status = r.status_code
        headers = r.headers
        url = re.sub(r"https?://(?:www\.)?", '', r.url).split("/")[0]
        data = r.raw.read(1049000, True).decode('UTF-8', 'replace')
    if headers.get('content-type', '').startswith('text/html'):
        soup = BeautifulSoup(data, 'html.parser')
        try:
            t = soup.title.string
            title = re.sub(r'[\t\r\n]', ' ', t)
            # Remove ASCII control characters
            title = re.sub(r'[\x00-\x1E\xA0\uefeff][^\x02\x03\x0F\x1D]', '', title)
            title = title.strip()
            title += "\x0F"
            if len(title) > 300:
                title = '{0}\x0F... (truncated)'.format(title[:300])
        except (AttributeError, TypeError) as e:
            if headers.get('content-type'):
                title = '\x0307{0}\x0F \x0303{1}\x0F'.format(status, headers['content-type'])
            else:
                title = '\x0307{0}\x0F \x0304[no title]\x0F'.format(status)
    else:
        if headers.get('content-type'):
            title = '\x0307{0}\x0F \x0303{1}\x0F'.format(status, headers['content-type'])
        else:
            title = '\x0307{0}\x0F \x0304[no title]\x0F'.format(status)
    return (title, url)

@add_hook
def titler(bot, event, irc, args):
    # Implementation taken from Eleos
    match = re.search(r"(?:https?://)(?:www\.)?([^\s]+)", " ".join(args))
    if match is not None:
        try:
            t, url = _get_title(match.group(0))
            title = "[{0!s}] - {1!s}".format(t, url)
        except requests.Timeout:
            title = '${RED}[timeout]${NORMAL}'
        except requests.TooManyRedirects:
            title = '${RED}[too many redirects]${NORMAL}'
        except Exception:
            title = '${RED}[error]${NORMAL}'
            print_error(irc, event)
        irc.reply(event, title)
