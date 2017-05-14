class Database(Object):
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

    def __getitem__(self, key):
        return self.userdb[key]
