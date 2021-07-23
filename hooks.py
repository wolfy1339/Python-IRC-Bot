from zirc.event import Event
from zirc.wrappers import connection_wrapper
from bot import Bot
from contextlib import closing
from bs4 import BeautifulSoup
import re
from utils.util import add_hook, print_error
import requests
import log
import utils
import config


@add_hook
def self_correct(bot: Bot, event: Event, irc: connection_wrapper, args: list[str]):
    if event.target in config.enable_correct:
        match = re.match(r"^s[/]([^/]+)[/]([^/]+)[/]?$", " ".join(args))
        if match is not None:
            nick = event.source.nick
            channel = event.target
            seen = bot.userdb[channel][nick]['seen']
            for i in range(len(seen)):
                msg = seen[i]['message']
                if re.match(r"^s[/]([^/]+)[/]([^/]+)[/]?$", msg) is not None:
                    pass
                else:
                    output = msg.replace(match.group(1), match.group(2))
                    if msg == output:
                        pass
                    else:
                        irc.reply(event, '<{0}> {1}'.format(nick, output))
                        log.info('Changing %s to %s', msg, output)
                        break
        else:
            pass


@add_hook
def user_correct(bot: Bot, event: Event, irc: connection_wrapper, args: list[str]):
    if event.target in config.enable_correct:
        match = re.match(r"^u[/]([^/]+)[/]([^/]+)[/]([^/]+)[/]?$", " ".join(args))
        if match is not None:
            nick = match.group(1)
            channel = event.target
            seen = bot.userdb[channel][nick]['seen']
            for i in range(len(seen)):
                msg = seen[i]['message']
                if re.match(r"^u[/]([^/]+)[/]([^/]+)[/]([^/]+)[/]?$", msg) is not None:
                    pass
                else:
                    output = msg.replace(match.group(2), match.group(3))
                    if msg == output:
                        pass
                    else:
                        irc.reply(event, '<{0}> {1}'.format(nick, output))
                        log.info('Changing %s to %s', args, output)
                        break
        else:
            pass


def _get_title(url: str):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/88.0'}

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
            title = re.sub(r'[\x00-\x01\x04-\x1C\x1E\ufeff\xbb\xbf\xef\xa0\xc2]', '', title)
            title = title.strip()
            title += "\x0F"
            if len(title) > 300:
                title = '{0}\x0F... (truncated)'.format(title[:300])
        except (AttributeError, TypeError):
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
def titler(bot: Bot, event: Event, irc: connection_wrapper, args: list[str]):
    if event.target in config.enable_titler:
        # Implementation taken from Eleos
        match = re.search(r"(?:https?://)(?:www\.)?([^\s]+)", " ".join(args))
        if match is not None:
            log.info(f'Fetching URL ({match.group(0)}) from user {event.source}')
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
