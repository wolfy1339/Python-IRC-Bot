import sys
import config
import log
import utils


class Events(object):
    def __init__(self, bot):
        self = bot
        # This might seem dumb, but the linters absolutely want it used
        self.config = bot.config

    @staticmethod
    def on_all(event, irc):
        if event.raw.startswith("ERROR"):
            log.error(" ".join(event.arguments))
        else:
            if event.raw.find("%") == -1:
                log.debug(event.raw)

    @staticmethod
    def on_ctcp(irc, event, raw):
        log.info("Received CTCP reply " + raw)

    def on_privmsg(self, event, irc, arguments):
        if " ".join(arguments).startswith(config.commandChar):
            utils.call_command(self, event, irc, arguments)

    @staticmethod
    def on_send(data):
        if data.find("%") == -1:
            log.debug(data)

    def on_nick(self, event, irc):
        nick = event.source.nick
        to_nick = event.arguments[0]
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
        nick = event.source.nick
        if nick == self.config['nickname']:
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
            self.removeEntry(event, nick)

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
            self.removeEntry(event, nick)

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
        if utils.checkPerms(hostmask, channel, trusted=True):
            log.info("Invited to %s by %s", channel, hostmask)
            irc.join(channel)

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
            self.addEntry(channel, nick, hostmask, host, account)

    def on_whospcrpl(self, event, irc, arguments):
        nick = arguments[3]
        if nick != "ChanServ":
            args = event.arguments
            (ident, host) = args[1:3]
            hostmask = "{0}!{1}@{2}".format(nick, ident, host)
            channel = args[0]
            account = args[4] if args[4] != "0" else None
            self.addEntry(channel, nick, hostmask, host, account)

    @staticmethod
    def on_315(event, irc):
        log.info("Received end of WHO reply from network")