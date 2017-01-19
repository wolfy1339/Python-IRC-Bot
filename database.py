def removeEntry(event):
    try:
        del self.userdb[event.target][event.source.nick]
    except KeyError:
        for i in self.userdb[event.target].values():
            if i['host'] == event.source.host:
                del self.userdb[event.target][i['hostmask'].split("!")[0]]
                break

def addEntry(channel, nick, hostmask, host, account):
    self.userdb[channel][nick] = {
        'hostmask': hostmask,
        'host': host,
        'account': account if account != "0" else None
    }
