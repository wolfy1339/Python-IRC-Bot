import sys
from zirc.test import TestCase
import log as logging
from utils import util
import commands
import config

logging.setLevel(30)

class fp(object):
    def __init__(self):
        self.irc_queue = []

class botTest(TestCase):
    def __init__(self):
        self.config = {}
        self.userdb = {}
        self.config['nickname'] = 'zIRC-test'
        self.fp = fp()

    def on_privmsg(self, event, irc, arguments):
        if " ".join(arguments).startswith(config.commandChar):
            util.call_command(self, event, irc, arguments)

    @staticmethod
    def on_kick(event, irc):
        nick = event.raw.split(" ")[3]
        if nick == 'zIRC-test':
            irc.join(event.target)

    @staticmethod
    def on_join(event, irc):
        irc.send("WHO {0} nuhs%nhua".format(event.target))

    @staticmethod
    def on_invite(event, irc):
        if util.checkPerms(event.source.host, event.target, trusted=True):
            irc.join(event.target)


bot = botTest()
log = """:user!~user@user/user PRIVMSG #zirc :Hey!
:bot!~limnoria@botters/wolf1339/bot/bigwolfy1339 NOTICE #zirc :Channel notice
:bot!~limnoria@botters/wolf1339/bot/bigwolfy1339 NOTICE zIRC-test :Priv notice
:user2!~user@user/user2 PRIVMSG #zirc :How are you?
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ban *!*@*
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?unban *!*@*
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?calc 1+1
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?calc
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?math 1+1
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?config ignores
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?cfg ignores
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?deop
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?echo moo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?flush
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?flushq
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?help
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?help kick
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?host
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ignore botters/wolf
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ignore botters/wolf random
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ignore botters/wolf 999
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ignore botters/wolf 999 #zirc
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?join ##foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?cycle
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?cycle #zirc
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?kick user,user2,user3
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?kick user, user2, user3
:wolfy1339!~wolfy1339@botters/wolfy PRIVMSG #zirc :?kick user, user2, user3
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?kick #zirc foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?list
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ls
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?list alias
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ls alias
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?log.level info
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?nick foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?op
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?part
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?part #zirc
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?perms
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ping
:wolfy1339bot!~wolfy1339@botters/wolfy/bot/mooobot PRIVMSG #zirc :?ping
:bot!~limnoria@botters/wolf1339/bot/bigwolfy1339 PRIVMSG ##wolfy1339 :?ping
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?quit
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?rainbow mooo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?remove foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?remove #zirc foo,moo,bo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?version
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?voice
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?unvoice
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?>> print("test")
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?py print("test")
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?eval print("test")
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?invalid
:user3!~user@user/user3 PRIVMSG zIRC-test :Hello there!"""

try:
    bot.start(log)
except Exception:
    logging.exception('An exception happened')
    sys.exit(-1)
