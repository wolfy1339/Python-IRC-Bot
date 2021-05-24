from zirc import Sasl, Caps
from os import getenv

# zIRC
ci = getenv('CI', 'false') == 'true'
if not ci:
    with open("password", "r") as i:
        password = i.read().strip()
    sasl = Sasl(username="BigWolfy1339", password=password, method="external")
    caps = Caps(sasl, "multi-prefix", "account-notify", "extended-join")

# IRC
channels = ["##wolfy1339", "#powder-bots", "#hellomouse", "#hellomouse-botwar"]
# Logging
logFormat = '%(levelname)s %(asctime)s %(message)s'
colorized = True
timestampFormat = '%Y-%m-%dT%H:%M:%S'
logLevel = 20  # INFO
stdoutWrap = True

# Bot
commandChar = '?'
owners = ['hellomouse/dev/wolfy1339']
admins = {
    'global': [],
    'channels': {
        '#hellomouse': []
    }
}
trusted = {
    'global': [],
    'channels': {
        '#hellomouse': []
    }
}
hooks_whitelist = ["#hellomouse", "##wolfy1339"]
bots = {
    'hosts': ['botters/wolf1339/bot/bigwolfy1339'],
    'channels': ['#hellomouse', '##wolfy1339']
}
ignores = {
    'global': [],
    'channels': {
        "#powder-bots": [],
        "##wolfy1339": [],
    }
}

# Error messages
noPerms = " ".join(["Sorry,",
                    "you do not have the right permissions",
                    "to execute this command"])
argsMissing = "Oops, looks like you forgot an argument there."
invalidCmd = 'Invalid command {0}'
tracebackPostError = "An error happened while trying to post the traceback"
secretEntry = "Are you sure you want this to be diplayed in a public channel?"
