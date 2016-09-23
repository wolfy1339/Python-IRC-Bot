import requests
import traceback
import six
from time import strftime, localtime
import logging
import ansi
import config

print_ = six.print_
PY3 = six.PY3
PY34 = six.PY34
PY2 = six.PY2
commands = {}
aliases = {}


def add_cmd(name, minArgs=1, alias=None, owner=False, admin=False):
    def real_command(func):
        global commands
        global aliases
        commands[name] = {
            'perms': [admin, owner],
            'function': func,
            'minArgs': minArgs
        }

        if alias:
            for i in alias:
                aliases[i] = {
                    'function': func,
                    'perms': [admin, owner],
                    'minArgs': minArgs
                }

    return real_command


def call_command(bot, event, irc, arguments):
    command = ' '.join(arguments).split(' ')
    args = command[1:] if len(command) > 1 else ''
    name = command[0][1:]
    try:
        cmd_perms = commands[name]['perms']
        minArgs = commands[name]['minArgs']
        host = event.source.host
        if checkPerms(host, owner=cmd_perms[0], admin=cmd_perms[1]):
            if not args and minArgs >= 1 or len(args) < minArgs:
                irc.reply(event, config.argsMissing)
            else:
                commands[name]['function'](bot, event, irc, args)
        else:
            irc.reply(event, config.noPerms)
    except KeyError:
        if not name == '' or name.find("?") != -1:
            irc.notice(event.source.nick, config.invalidCmd.format(name))
    except Exception:
        irc.reply(event, 'Oops, an error occured!')
        PrintError(irc, event)
    else:
        privmsg = event.target == bot.config['nickname']
        target = "a private message" if privmsg else event.target
        logging.info("{0} called {1} in {2}".format(event.source, name, target))


def checkPerms(host, owner=False, admin=False):
    isOwner = host in config.owners
    isAdmin = host in config.admins
    isIgnored = host in config.ignores
    if owner and isOwner and not isIgnored:
        return True
    elif admin and (isAdmin or isOwner) and not isIgnored:
        return True
    elif not owner and not admin and not isIgnored:
        return True
    else:
        return False


def PrintError(irc, event):
    print_(ansi.RED, traceback.format_exc(), ansi.RESET, flush=True)
    try:
        r = requests.post("http://dpaste.com/api/v2/",
                          data={
                              "content": str(traceback.format_exc()),
                              "expiry-days": "10"
                            },
                          allow_redirects=True,
                          timeout=60)
        irc.msg('##wolfy1339', "Error: {0}".format(r.text.split("\n")[0]))
    except Exception:
        irc.msg('##wolfy1339', "An error happened while trying to post the traceback")
        print_(ansi.RED, traceback.format_exc(), ansi.RESET, flush=True)
