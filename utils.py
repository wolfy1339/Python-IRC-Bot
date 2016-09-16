commands = {}

def add_cmd(name, alias=None, owner=False, admin=False):
    def real_command(func):
        commands[name] = func
        if alias:
            commands[alias] = func

    return real_command


def call_command(bot, event, irc):
    command = ' '.join(event.arguments).split(' ')
    args = command[1]
    name = command[0][1:]
    try:
        commands[name](bot, event, irc, args)
    except KeyError:
        irc.reply(event, 'Invalid command {}'.format(name))
    except:
        irc.reply(event, 'Oops, an error occured')

