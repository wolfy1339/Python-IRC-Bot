import requests
import traceback
import six
import logging
import ansi
import config

print_ = six.print_
PY3 = six.PY3
PY34 = six.PY34
PY2 = six.PY2
commands = {}
cmd_list = []
alias_list = []


def add_cmd(name, minArgs=1, alias=None, owner=False, admin=False, trusted=False, hide=False):
    def real_command(func):
        global commands
        global cmd_list
        global alias_list

        commands[name] = {
            'perms': [trusted, admin, owner],
            'func': func,
            'minArgs': minArgs,
            'hide': hide
        }

        if alias:
            for i in alias:
                commands[i] = {
                    'perms': [trusted, admin, owner],
                    'func': func,
                    'minArgs': minArgs,
                    'hide': True
                }
                alias_list.append(i)

        cmds = [i for i in commands.keys() if not commands[i]['hide']]
        cmd_list = sorted(cmds)
        alias_list = sorted(alias_list)

    return real_command


def call_command(bot, event, irc, arguments):
    command = ' '.join(arguments).split(' ')
    name = command[0][1:]
    if not name == '' or not name.find("?") != -1:
        privmsg = event.target == bot.config['nickname']
        args = command[1:] if len(command) > 1 else ''

        try:
            perms = commands[name]['perms']
            minArgs = commands[name]['minArgs']
            host = event.source.host
            chan = event.target if not privmsg else False

            if checkPerms(host, owner=perms[2], admin=perms[1], trusted=perms[0], channel=chan):
                if len(args) < minArgs:
                    irc.reply(event, config.argsMissing)
                else:
                    commands[name]['func'](bot, event, irc, args)
            else:
                irc.reply(event, config.noPerms)
        except KeyError:
            irc.notice(event.source.nick, config.invalidCmd.format(name))
        except Exception:
            irc.reply(event, 'Oops, an error occured!')
            PrintError(irc, event)
        else:
            target = "a private message" if privmsg else event.target
            logging.info("%s called %s in %s", event.source, name, target)


def checkPerms(host, owner=False, admin=False, trusted=False, channel=False):
    isOwner = host in config.owners
    isAdmin = host in config.admins
    isTrusted = host in config.trusted
    isBot = host.find("bot") != -1 and host not in config.bots['hosts']
    ignores = config.ignores["global"]

    ignoreChans = list(config.ignores["channels"].keys())

    if channel:
        if channel in ignoreChans:
            ignores.extend(config.ignores["channels"][channel])

        if channel in config.bots['channels']:
            isBot = False
    isIgnored = host in ignores

    if owner and isOwner:
        return True
    elif admin and (isAdmin or isOwner):
        return True
    elif trusted and (isTrusted or isAdmin or isOwner) and not isIgnored:
        return True
    elif not (owner or admin or trusted) and not isIgnored and not isBot:
        return True
    else:
        return False


def PrintError(irc, event):
    print_(ansi.RED, traceback.format_exc(), ansi.RESET, flush=True)
    try:
        syntax = "py3tb" if PY3 else "pytb"
        r = requests.post("http://dpaste.com/api/v2/",
                          data={
                              "content": str(traceback.format_exc()),
                              "syntax": syntax,
                              "expiry-days": "10"
                            },
                          allow_redirects=True,
                          timeout=60)
        irc.msg('##wolfy1339', "Error: {0}".format(r.text.split("\n")[0]))
    except Exception:
        irc.msg('##wolfy1339', config.tracebackPostError)
        print_(ansi.RED, traceback.format_exc(), ansi.RESET, flush=True)
