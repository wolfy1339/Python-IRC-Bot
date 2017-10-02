import log

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
        for nick in names.split():
            nick = nick.lstrip(''.join(list(
                               self.server['ISUPPORT']['PREFIX'].values())))
            if nick not in self.channels[channel]['names']:
                self.channels[channel][nick]['modes']

    @staticmethod
    def on_endofnames(event, irc):
        log.info('Received end of NAMES reply.')

    @staticmethod
    def on_315(event, irc):
        log.info("Received end of WHO reply from network")
