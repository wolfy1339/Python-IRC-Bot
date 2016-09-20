import requests
import traceback
import six

print_ = six.print_
PY3 = six.PY3
PY34 = six.PY34
PY2 = six.PY2
commands = {}
perms = {}


def add_cmd(name, alias=None, owner=False, admin=False):
    def real_command(func):
        global commands
        global perms
        commands[name] = func
        perms[name] = [admin, owner]
        if alias:
            if isinstance(alias, list):
                for i in alias:
                    commands[i] = func
            else:
                commands[alias] = func

    return real_command


def call_command(bot, event, irc, arguments):
    command = ' '.join(arguments).split(' ')
    args = ' '.join(command[1:]) if len(command) > 1 else None
    name = command[0][1:]
    try:
        cmd_perms = perms[name]
        host = event.source.host
        if checkPerms(host, owner=cmd_perms[0], admin=cmd_perms[1]):
            if not name == "help" and args is None:
                irc.reply(event, "Oops, looks like you forgot an argument here")
            else:
                commands[name](bot, event, irc, args)
        else:
            irc.reply(event, "Sorry, you do not have the right permissions to execute this command")
    except KeyError:
        irc.reply(event, 'Invalid command {0}'.format(name))
    except Exception as e:
        irc.reply(event, 'Oops, an error occured!')
        irc.reply(event, repr(e))
        PrintError(irc, event)
    else:
        privmsg = event.target == bot.config['nickname']
        target = "a private message" if privmsg else event.target
        print_("{0} called {1} in {2}".format(event.source, name, target), flush=True)


def checkPerms(host, owner=False, admin=False):
    owner_list = ['botters/wolfy1339']
    admin_list = []
    if owner and host in owner_list:
        return True
    elif admin and host in admin_list or admin and host in owner_list:
        return True
    elif not owner and not admin:
        return True
    else:
        return False


def PrintError(irc, event):
    print_(traceback.format_exc())
    irc.reply(event, "Error printed to console")
    try:
        r = requests.post("http://dpaste.com/api/v2/",
                          data={
                              "content": str(traceback.format_exc()),
                              "expiry-days": "10"
                            },
                          allow_redirects=True,
                          timeout=60)
        irc.reply(event, "Error: {0}".format(r.text.split("\n")[0]))
    except Exception:
        irc.reply(event, "An error happened while trying to post the traceback")
        print_(traceback.format_exc(), flush=True)
