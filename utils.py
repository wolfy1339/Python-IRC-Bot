commands = {}
perms = {}

def add_cmd(name, alias=None, owner=False, admin=False):
    def real_command(func):
        global commands
        global perms
        commands[name] = func
        perms[name] = [admin, owner]
        if alias:
            commands[alias] = func

    return real_command


def call_command(bot, event, irc):
    command = ' '.join(event.arguments).split(' ')
    args = ' '.join(command[1:]) if len(command) > 1 else None
    name = command[0][1:]
    try:
        cmd_perms = perms[name]
        host = event.source.host
        if checkPerms(host, owner=cmd_perms[0], admin=cmd_pemrms[1]):
            commands[name](bot, event, irc, args)
    except KeyError:
        irc.reply(event, 'Invalid command {}'.format(name))
    except Exception:
        irc.reply(event, 'Oops, an unknown error occured')
    else:
        privmsg = event.target == bot.config['nickname']
        target = "a private message" if privmsg else event.target
        print("{} called {} in {}".format(event.source, name, target))

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

