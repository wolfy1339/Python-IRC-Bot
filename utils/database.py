import json


class Database(dict):
    """Holds a dict that contains all the information about the users in a channel"""
    def __init__(self, irc):
        super(Database, self).__init__(json.load(open("userdb.json")))
        self.irc = irc

    def remove_entry(self, event, nick):
        try:
            del self[event.target][nick]
        except KeyError:
            for i in self[event.target].values():
                if i['host'] == event.source.host:
                    del self[event.target][i['hostmask'].split("!")[0]]
                    break

    def add_entry(self, channel, nick, hostmask, account):
        temp = {
            'hostmask': hostmask,
            'host': hostmask.split("@")[1],
            'account': account,
            'seen': [__import__("time").time(), ""]
        }
        if nick in self[channel]:
            del temp['seen']
            self[channel][nick].update(temp)
        else:
            self[channel][nick] = temp

    def get_user_host(self, channel, nick):
        try:
            host = "*!*@" + self[channel][nick]['host']
        except KeyError:
            self.irc.send("WHO {0} nuhs%nhuac".format(channel))
            host = "*!*@" + self[channel][nick]['host']
        return host

    def flush(self):
        with open('userdb.json', 'w') as f:
            json.dump(self, f, indent=2, separators=(',', ': '))
            f.write("\n")
