from zirc.test import TestCase
import log
import utils
import commands
import config

class botTest(TestCase):
    def on_privmsg(self, event, irc, arguments):
        if " ".join(arguments).startswith(config.commandChar):
            utils.call_command(self, event, irc, arguments)

    def on_kick(self, event, irc):
        nick = event.raw.split(" ")[3]
        if nick == self.config['nickname']:
            logging.warning("Kicked from %s, trying to re-join", event.target)
            irc.join(event.target)

    def on_join(self, event, irc):
        log.info("Joining %s", event.target)
        irc.send("WHO {0} nuhs%nhu".format(event.target))

    def on_invite(self, event, irc):
        if utils.checkPerms(event.source.host, trusted=True):
            hostmask = event.source.hostmask
            log.info("Invited to %s by %s", event.target, hostmask)
            irc.join(event.target)


bot = botTest()
log = """:user!~user@user/user PRIVMSG #zirc :Hey!
:user2!~user@user/user2 PRIVMSG #zirc :How are you?
:user3!~user@user/user3 PRIVMSG zIRC-test :Hello there!"""
bot.start(log)
