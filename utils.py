import requests
import traceback

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
            commands[name](bot, event, irc, args)
    except KeyError:
        irc.reply(event, 'Invalid command {}'.format(name))
    except Exception as e:
        irc.reply(event, 'Oops, an error occured!')
        irc.reply(event, repr(e))
        PrintError(event)
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

def PrintError(event):
    print("=======ERROR=======\n{0}========END========\n".format(traceback.format_exc()))
    irc.reply(event, "Error printed to console")
    try:
        r = requests.post("http://dpaste.com/api/v2/", data={"content": traceback.format_exc(), "expiry-days":"10"}, allow_redirects=True, timeout=60)
        irc.reply(event, "Error: {1}".format(r.text.split("\n")[0]))
    except Exception:
        irc.reply(event, "We heard you like errors, so we put an error in your error handler so you can error while you catch errors")
        print("=======ERROR=======\n{0}========END========\n".format(traceback.format_exc()))
