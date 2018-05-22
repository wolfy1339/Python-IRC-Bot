import sys
from zirc.test import TestCase
from zirc.wrappers import connection_wrapper
import log as logging
from utils import util
from utils import database
import config

config.admins['global'].append("user/user3")
config.trusted['global'].append("user/user2")
config.hooks_whitelist.append('#zirc')
logging.setLevel(30)

class fp(object):
    def __init__(self):
        self.irc_queue = []

class Undefined(object):
    @staticmethod
    def stop():
        return None

class botTest(TestCase):
    def __init__(self):
        self.config = {}
        self.config['nickname'] = 'zIRC-test'
        self.userdb = database.Database(self)
        self.userdb.add_entry("#zirc", "wolfy1339", 'wolfy1339!~wolfy1339@botters/wolfy1339', 'wolfy1339')
        self.userdb.add_entry("#zirc", "user", 'user!~user@user/user', 'user')
        self.userdb.add_entry("#zirc", "user2", 'user2!~user@user/user2', 'user2')
        self.userdb.add_entry("#zirc", "user3", 'user3!~user@user/user3', 'user3')
        self.userdb.add_entry("#zirc", "user4", 'user4!~user@user/user4', 'user4')
        self.userdb.add_entry("#zirc", "user5", 'user5!~user@user/user5', 'user5')
        self.userdb.add_entry("#zirc", "wuser", "wuser!~wolfy1339@unaffiliated/wolfy", None)
        self.userdb.add_entry("#zirc", "wolfy1339bot", "wolfy1339bot!~wolfy1339@botters/wolfy/bot/mooobot", None)
        self.userdb.add_entry("##wolfy1339", "bot", "bot!~limnoria@botters/wolf1339/bot/bigwolfy1339", "BigWolfy1339")
        self.fp = fp()
        self.web = Undefined()
        self.db_job = Undefined()
        # Event handlers
        util.reload_handlers(self)


bot = botTest()
log = """:user!~user@user/user PRIVMSG #zirc :Hey!
:bot!~limnoria@botters/wolf1339/bot/bigwolfy1339 NOTICE #zirc :Channel notice
:bot!~limnoria@botters/wolf1339/bot/bigwolfy1339 NOTICE zIRC-test :Priv notice
:user2!~user@user/user2 PRIVMSG #zirc :How are you?
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?>> print(self.userdb)
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?>> self.userdb.get("#zirc")
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?>> self.userdb.get("##wolfy1339")
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ban *!*@*
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ban *!*@*,*!*@user/*,user3
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ban wolfy1339
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?unban *!*@*
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?calc 1+1
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?calc
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?calc 2+3***sqrt(4)
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?calc 2+3*sqrt(4)
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?calc 2+3^200
:user!~user@user/user PRIVMSG #zirc :Please stop the bot spam, we can hardly hear each other!
:user!~user@user/user PRIVMSG #zirc :s/bot/moo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?math 1+1
:user2!~user@user/user2 PRIVMSG #zirc :What was that?
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?cfg ignores
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?config ignores
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?config invalid
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?config invalid None
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?config trusted {'global':["user/user2"],'channels':{}}
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?config password
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?config tracebackPostError BigWolfy1339
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?cycle
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?cycle #zirc
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?deop
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?deop foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?echo moo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?eval self.userdb["##wolfy1339"] = {}
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?eval Undefined
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?eval dir(self)
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?flush
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?flushq
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?hash sha224 moo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?hash invalid moo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?help
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?help kick
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?help invalid
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?host
:doggy!~user@user/user NICK :user
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ignore botters/wolf
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ignore botters/wolf random
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ignore botters/wolf 999
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ignore botters/wolf 999 #zirc
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?join ##foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?kban #zirc GTFO! user
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?kban #zirc GTFO! user1,user2,user3
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?kick user,user2,user3
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?kick user, user2, user3
:wuser!~wolfy1339@unaffiliated/wolfy PRIVMSG #zirc :?kick user, user2, user3
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?kick #zirc foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?leave #zirc
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?leave
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?list
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?list alias
:wuser!~wolfy1339@unaffiliated/wolfy PRIVMSG #zirc :?list
:user2!~user@user/user2 PRIVMSG #zirc :?list
:user3!~user@user/user3 PRIVMSG #zirc :?list
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?log.level
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?log.level debug
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?log.level info
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?log.level error
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?log.level warning
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?log.level critical
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?log.level exception
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ls
:user4!~user@user/user4 PART #zirc :Undefined
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ls alias
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?math 2**2
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?md5 moo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?nick foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ninja #zirc foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?op
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?op user2
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?part
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?part #zirc
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?perms
:bot!~limnoria@botters/wolf1339/bot/bigwolfy1339 PRIVMSG ##wolfy1339 :?perms
:wuser!~wolfy1339@unaffiliated/wolfy PRIVMSG #zirc :?perms
:user2!~user@user/user2 PRIVMSG #zirc :?perms
:user3!~user@user/user3 PRIVMSG #zirc :?perms
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ping
:wolfy1339bot!~wolfy1339@botters/wolfy/bot/mooobot PRIVMSG #zirc :?ping
:bot!~limnoria@botters/wolf1339/bot/bigwolfy1339 PRIVMSG ##wolfy1339 :?ping
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?py print("test")
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?quit
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?rainbow mooo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?rejoin
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?rejoin #zirc
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?reload plugins
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?reload commands
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?reload config
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?remove foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?remove #zirc foo,moo,bo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?sha1 moo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?sha256 moo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?sha384 moo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?sha512 moo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?unban
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?unban foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?unban #zirc foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?unvoice
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?unvoice foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?unvoice #zirc foo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?version
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?voice
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?voice user3
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?invalid
@time=2011-10-19T16:40:51.620Z;account=user3 :user3!~user@user/user3 QUIT :Hello there!
:woof!~user@user/user5 PART #zirc :*.net *.split"""

try:
    bot.start(log)
except Exception:
    logging.exception('An exception happened')
    sys.exit(-1)
