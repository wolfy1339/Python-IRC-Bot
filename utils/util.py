import traceback
import re
import requests
import six

import config
import log
from .ignores import check_ignored

print_ = six.print_
PY2 = six.PY2
PY3 = six.PY3
PY34 = six.PY34
commands = {}
cmd_list = []
alias_list = []
hooks = []

get = requests.get
post = requests.post


def is_ip_or_rdns(host):
    ip = re.match(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}", host)
    url = re.match(r"(?:https?\:\/\/)?[-\w@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-\w@:%_\+.~#?&//=]*)", host)
    return ip is not None or url is not None


def add_cmd(name, min_args=1, alias=None, owner=False,
            admin=False, trusted=False, hide=False):
    def real_command(func):
        global alias_list
        global cmd_list

        commands[name] = {
            'perms': [trusted, admin, owner],
            'func': func,
            'minArgs': min_args,
            'hide': hide
        }

        if alias:
            for i in alias:
                commands[i] = commands[name]
                commands[i]['hide'] = True
                alias_list.append(i)

        cmds = [i for i in commands.keys() if not commands[i]['hide']]
        cmd_list = sorted(cmds)
        alias_list = sorted(alias_list)

    return real_command


def call_command(bot, event, irc, arguments):
    command = ' '.join(arguments).split(' ')
    if not command[0].startswith(config.commandChar):
        del command[0]
        name = command[0]
    else:
        name = command[0][1:]
    if not name == '' and not name.find("?") != -1:
        privmsg = event.target == bot.config['nickname']
        args = command[1:] if len(command) > 1 else ''

        host = event.source.host
        chan = event.target if not privmsg else False

        try:
            perms = commands[name]['perms']
            min_args = commands[name]['minArgs']

            if check_perms(event, chan, owner=perms[2], admin=perms[1],
                           trusted=perms[0]) or name == 'shrug' and event.source.host.startswith("hellomouse/bin/notJeffbot"):
                if len(args) < min_args:
                    irc.reply(event, config.argsMissing)
                else:
                    target = "a private message" if privmsg else event.target
                    source = event.source
                    log.info("%s called %s in %s", source, name, target)
                    commands[name]['func'](bot, event, irc, args)
            else:
                if not event.source.host.find("/bot/"):
                    irc.reply(event, config.noPerms)
        except KeyError:
            irc.notice(event.source.nick, config.invalidCmd.format(name))
        except Exception:
            irc.reply(event, 'Oops, an error occured!')
            print_error(irc, event)


def add_hook(func):
    hooks.append(func)


def isBot(event):
    is_Eleos = event.source.host == "kalahari.sigint.pw" and event.source.user == "bot"
    is_Jenni = event.source.user == "~jenni" and event.source.host.startswith("jenni")
    is_Celena = event.source.host == "techcavern/bot"
    is_tacgnol = event.source.host == "2607:2200:0:2347:0:3353:f8:7d39" and event.source.user == "~mouses"
    is_hellomouse_bots = event.source.host.startswith("hellomouse/bin/")
    is_bot = event.source.host.find("/bot/") != -1 or is_Eleos or is_Jenni or is_Celena or is_hellomouse_bots
    return is_bot


def call_hook(bot, event, irc, args):
    if event.target in config.hooks_whitelist and not isBot(event):
        try:
            for i in hooks:
                i(bot, event, irc, args)
        except Exception:
            irc.reply(event, 'Oops, an error occured!')
            print_error(irc, event)


def check_perms(event, channel, owner=False, admin=False, trusted=False):
    admins = config.admins['global']
    trustees = config.trusted['global']

    admins += config.admins['channels'].get(channel, [])
    trustees += config.trusted['channels'].get(channel, [])

    is_owner = event.source.host in config.owners
    is_admin = event.source.host in admins
    is_trusted = event.source.host in trustees
    is_bot = isBot(event)
    if channel in config.bots['channels']:
        is_bot = False
    is_ignored = check_ignored(event.source.host, channel)

    if owner and is_owner:
        return True
    elif admin and (is_admin or is_owner):
        return True
    elif trusted and (is_trusted or is_admin or is_owner) and not is_ignored:
        return True
    elif not (owner or admin or trusted) and not is_ignored and not is_bot:
        return True
    return False


def reload_handlers(bot):
    bot.events = __import__("handlers").Events(bot)
    for h in dir(bot.events):
        func = getattr(bot.events, h)
        if (callable(func) or h == "server") and not h.startswith("__"):
            setattr(bot, h, func)


def print_error(irc, event):
    log.exception("An unknown error occured")
    if not config.ci:
        try:
            syntax = "py3tb" if PY3 else "pytb"
            tb = traceback.format_exc().strip()
            title = "zIRCBot Error: {0}"
            data = {
                "title": title.format(tb.split("\n")[-1]),
                "content": tb,
                "syntax": syntax,
                "expiry-days": "10",
                "poster": "wolfy1339"
            }
            r = post("http://dpaste.com/api/v2/",
                     data=data,
                     allow_redirects=True,
                     timeout=60)
            irc.msg('##wolfy1339', f"Error: {r.text.split("\n")[0]}")
        except Exception:
            irc.msg('##wolfy1339', config.tracebackPostError)
            log.exception(config.tracebackPostError)
    else:
        __import__('sys').exit(1)
