from zirc import Sasl

# zIRC
sasl = Sasl(username="BigWolfy1339", password="")

# IRC
channels = ["##wolfy1339", "##powder-bots", "##jeffl35"]

# Logging
logFormat = '%(levelname)s %(asctime)s %(message)s'
colorized = True
timestampFormat = '%Y-%m-%dT%H:%M:%S'
logLevel = 20 # INFO

# Bot
commandChar = '?'
owners = ['botters/wolfy1339']
admins = []
trusted = []
bots = {
    'hosts': ['botters/wolf1339/bot/bigwolfy1339'],
    'channels': ['##jeffl35', '##wolfy1339']
}
ignores = {
    'global': [],
    'channels': {
        "##powder-bots": [],
        "##wolfy1339": [],
    }
}

# Error messages
noPerms = "Sorry, you do not have the right permissions to execute this command"
argsMissing = "Oops, looks like you forgot an argument there."
invalidCmd = 'Invalid command {0}'
tracebackPostError = "An error happened while trying to post the traceback"
