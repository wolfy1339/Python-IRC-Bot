import log
from utils import util


class User(object):
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

    # Account tracking
    def on_account(self, event, irc, arguments):
        self.userdb.change_attr(event.source.nick, 'account', event.target)

    def on_whoreply(self, event, irc, arguments):
        nick = arguments[4]
        if nick != "ChanServ":
            (ident, host) = arguments[1:3]
            channel = arguments[0]
            hostmask = "{0}!{1}@{2}".format(nick, ident, host)
            if "gateway" not in host or not util.is_ip_or_rdns(host):
                account = host.split("/")[-1].split('.')[-1]
            else:
                account = None
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

    def on_namereply(self, event, irc, arguments):
        channel = event.arguments[1]
        names = event.arguments[2]
        # This is only possible due to multi-prefix CAP
        for value in names.split():
            nick = value.lstrip(''.join(list(
                               self.server['ISUPPORT']['PREFIX'].values())))
            modes = ''
            if '@' in value:
                modes += "o"
            elif '+' in value:
                modes += "v"
            self.userdb[channel][nick]['modes'] = modes

    @staticmethod
    def on_endofnames(event, irc):
        log.info('Received end of NAMES reply.')

    @staticmethod
    def on_315(event, irc):
        log.info("Received end of WHO reply from network")
