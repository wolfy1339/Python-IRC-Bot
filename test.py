from zirc.test import TestCase
import log as logging
import utils
import commands
import config

logging.setLevel(10)

class botTest(TestCase):
    def __init__(self):
        self.config = {}
        self.config['nickname'] = 'zIRC-test'

    def on_all(event, irc):
        logging.debug(event.source)

    def on_privmsg(self, event, irc, arguments):
        if " ".join(arguments).startswith(config.commandChar):
            utils.call_command(self, event, irc, arguments)

    def on_kick(self, event, irc):
        nick = event.raw.split(" ")[3]
        if nick == 'zIRC-test':
            logging.warning("Kicked from %s, trying to re-join", event.target)
            irc.join(event.target)

    def on_join(self, event, irc):
        logging.info("Joining %s", event.target)
        irc.send("WHO {0} nuhs%nhu".format(event.target))

    def on_invite(self, event, irc):
        if utils.checkPerms(event.source.host, trusted=True):
            hostmask = event.source.hostmask
            logging.info("Invited to %s by %s", event.target, hostmask)
            irc.join(event.target)


bot = botTest()
log = """:user!~user@user/user PRIVMSG #zirc :Hey!
:user2!~user@user/user2 PRIVMSG #zirc :How are you?
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ban
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?calc
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?config
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?cycle
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?deop
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?echo
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?help
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?host
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?join
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?kban
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?kick
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?list
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?log.level
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?nick
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?op
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?part
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?perms
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?ping
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?quit
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?rainbow
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?reload
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?unban
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?unvoice
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?version
:wolfy1339!~wolfy1339@botters/wolfy1339 PRIVMSG #zirc :?voice
:user3!~user@user/user3 PRIVMSG zIRC-test :Hello there!"""
bot.start(log)
