class Database(object):
    def __init__(self, channels):
        self.userdb = {}
        for i in channels:
            self.userdb[i] = {}
        self.__getitem__ = self.userdb.__getitem__
        self.__delitem__ = self.userdb.__delitem__
        self.__setitem__ = self.userdb.__setitem__
        self.__str__ = self.userdb.__str__
        self.get = self.userdb.get
        self.keys = self.userdb.keys

    def removeEntry(self, event, nick):
        try:
            del self.userdb[event.target][nick]
        except KeyError:
            for i in self.userdb[event.target].values():
                if i['host'] == event.source.host:
                    nick = i['hostmask'].split("!")[0]
                    del self.userdb[event.target][nick]
                    break

    def addEntry(self, channel, nick, hostmask, host, account):
        self.userdb[channel][nick] = {
            'hostmask': hostmask,
            'host': host,
            'account': account
        }
