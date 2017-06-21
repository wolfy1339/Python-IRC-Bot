import datetime
import sys
import time
import config
# This is required so that util.call_command works
import plugins  # pylint: disable=unused-import
import log
from utils import util

strptime = datetime.datetime.strptime
class Events(object):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.bot.config
        self.userdb = self.bot.userdb

    @staticmethod
    def on_all(event, irc, arguments):
        if event.raw.startswith("ERROR"):
            log.error(" ".join(event.arguments))
            if " ".join(event.arguments).startswith("Closing Link"):
                import json
                with open("userdb.json", "r") as f:
                    json.dump(self.userdb, f, indent=2, separators=(',', ': '))
                sys.exit(1)
        else:
            if event.raw.find("%") == -1:
                log.debug(event.raw)

    @staticmethod
    def on_ctcp(irc, event, raw):
        log.info("Received CTCP reply " + raw)

    def on_privmsg(self, event, irc, arguments):
        nick = event.source.nick
        str_args = ' '.join(arguments)
        if len(event.tags):
            for i in event.tags:
                try:
                    f = '%Y-%m-%dT%H:%M:%S.%f'
                    timestamp = strptime(i['time'], f).timetuple()
                    timestamp = time.mktime(timestamp)
                except KeyError:
                    pass
        else:
            timestamp = time.time()
        self.userdb[event.target][nick]['seen'] = [timestamp, str_args]
        if " ".join(arguments).startswith(config.commandChar):
            util.call_command(self.bot, event, irc, arguments)
        else:
            util.call_hook(self.bot, event, irc, arguments)

    @staticmethod
    def on_send(data):
        if data.find("%") == -1:
            log.debug(data)

    def on_nick(self, event, irc):
        to_nick = event.source.nick
        nick = event.arguments[0]
        for chan in self.userdb.keys():
            chandb = self.userdb[chan]
            for u in chandb.values():
                if u['host'] == event.source.host:
                    self.userdb[chan][to_nick] = chandb[nick]
                    self.userdb[chan][to_nick]['hostmask'] = event.source
                    del self.userdb[chan][nick]
                    break
            break

    def on_quit(self, event, irc):
        import json
        nick = event.source.nick
        if nick == self.config['nickname']:
            with open("userdb.json", "r") as f:
                json.dump(self.userdb, f, indent=2, separators=(',', ': '))
            sys.exit(1)
        else:
            for chan in self.userdb.keys():
                for u in self.userdb[chan].values():
                    if u['host'] == event.source.host:
                        del self.userdb[chan][nick]
                        break
                break

    def on_kick(self, event, irc):
        nick = event.raw.split(" ")[3]
        if nick == self.config['nickname']:
            log.warning("Kicked from %s, trying to re-join", event.target)
            irc.join(event.target)
        else:
            self.userdb.remove_entry(event, nick)

    def on_part(self, event, irc):
        requested = "".join(event.arguments).startswith("requested")
        nick = event.source.nick
        if nick == self.config['nickname']:
            if requested:
                log.warning("Removed from %s, trying to re-join", event.target)
                irc.join(event.target)
            else:
                del self.userdb[event.target]
        else:
            self.userdb.remove_entry(event, nick)

    def on_join(self, event, irc):
        if event.source.nick == self.config['nickname']:
            log.info("Joining %s", event.target)
            self.userdb[event.target] = {}
            irc.send("WHO {0} nuhs%nhuac".format(event.target))
        else:
            irc.send("WHO {0} nuhs%nhuac".format(event.source.nick))

    @staticmethod
    def on_invite(event, irc):
        hostmask = event.source.host
        channel = event.arguments[0]
        if util.check_perms(hostmask, channel, trusted=True):
            log.info("Invited to %s by %s", channel, hostmask)
            irc.join(channel)

    def on_notice(self, event, irc):
        source = event.source.host
        if not event.target == "*":
            if not event.target == self.config['nickname']:
                channel = event.target
                log.info("Received channel notice from %s in %s", source, channel)
            else:
                log.info("Received private notice from %s", source)

    # Numeric events
    def on_unavailresource(self, event, irc):
        log.error("Nick unavailable, trying alternative")
        irc.nick(self.config['nickname'] + "_")
        self.config['nickname'] = self.config['nickname'] + "_"

    def on_nicknameinuse(self, event, irc):
        log.error("Nick already in use, trying alternative")
        irc.nick(self.config['nickname'] + "_")
        self.config['nickname'] = self.config['nickname'] + "_"

    @staticmethod
    def on_bannedfromchan(event, irc):
        s = event.raw.split(" ")
        channel = s[3]
        irc.notice("wolfy1339", "Banned from {0}".format(channel))
        log.warning("Banned from %s", channel)

    @staticmethod
    def on_endofmotd(event, irc):
        log.info("Received MOTD from network")

    @staticmethod
    def on_welcome(event, irc):
        log.info("Connected to network")

    def on_whoreply(self, event, irc, arguments):
        nick = arguments[4]
        if nick != "ChanServ":
            (ident, host) = arguments[1:3]
            channel = arguments[0]
            hostmask = "{0}!{1}@{2}".format(nick, ident, host)
            account = host.split("/")[-1].split('.')[-1]
            self.userdb.add_entry(channel, nick, hostmask, account)

    def on_whospcrpl(self, event, irc, arguments):
        nick = arguments[3]
        if nick != "ChanServ":
            args = event.arguments
            (ident, host) = args[1:3]
            hostmask = "{0}!{1}@{2}".format(nick, ident, host)
            channel = args[0]
            account = args[4] if args[4] != "0" else None
            self.userdb.add_entry(channel, nick, hostmask, account)

    @staticmethod
    def on_315(event, irc):
        log.info("Received end of WHO reply from network")
