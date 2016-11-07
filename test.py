from zirc.test import TestCase
import utils
import commands
import config

class botTest(TestCase):
    def on_privmsg(self, event):
        if " ".join(arguments).startswith(config.commandChar):
            utils.call_command(self, event, irc, arguments)

bot = botTest()
log = """:user!~user@user/user PRIVMSG #zirc :Hey!
:user2!~user@user/user2 PRIVMSG #zirc :How are you?
:user3!~user@user/user3 PRIVMSG zIRC-test :Hello there!"""
bot.start(log)
