class Database(object):
    def __init__(self, channels):
        self.userdb = {}
        for i in channels:
            self.userdb[i] = {}

    def removeEntry(self, event, nick):
        try:
            del self.userdb[event.target][nick]
        except KeyError:
            for i in self.userdb[event.target].values():
                if i['host'] == event.source.host:
                    del self.userdb[event.target][i['hostmask'].split("!")[0]]
                    break

    def addEntry(self, channel, nick, hostmask, host, account):
        self.userdb[channel][nick] = {
            'hostmask': hostmask,
            'host': host,
            'account': account
        }

    __getitem__ = self.userdb.__getitem__
    __delitem__ = self.userdb.__delitem__
    __setitem__ = self.userdb.__setitem__
    __str__ = self.userdb.__str__

    get = self.userdb.get

    def keys(self):
        return self.userdb.keys()
