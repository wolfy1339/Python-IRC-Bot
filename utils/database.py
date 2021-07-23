import json
import copy
from typing import Optional, TypeVar, TypedDict
from zirc.event import Event

from zirc.wrappers import connection_wrapper

class SeenDB(TypedDict):
    time: float
    message: str

class UserDB(TypedDict):
    hostmask: str
    host: str
    account: str
    modes: str
    seen: list[SeenDB]

_KT = TypeVar("_KT", bound=str) #  key type
_VT = TypeVar("_VT", bound=dict[str, UserDB]) #  value type

class Database(dict[_KT, _VT]):
    """Holds a dict that contains all the information
    about the users and their last seen actions in a channel"""

    def __init__(self, bot):
        with open("userdb.json") as f:
            super(Database, self).__init__(json.load(f))

        class x():
            def __init__(self, bot):
                self._config = bot.config
                self.send = bot.send
        self.irc = connection_wrapper(x(bot))

    def change_attr(self, name: str, attr: str, value: str, channel: Optional[str]=None):
        if channel is not None:
            self[channel][name][attr] = value
        for i in self:
            try:
                if attr == "host":
                    nick_ident = self[i][name]["hostmask"].split("@")[0]
                    self[i][name]["hostmask"] = f'{nick_ident}@{value}'
                    self[i][name][attr] = value
                elif attr == "ident":
                    self[i][name]["hostmask"] = f'{name}!{value}@{self[i][name]["host"]}'
                else:
                    self[i][name][attr] = value
            except KeyError:
                pass

    def remove_entry(self, event: Event, nick: str):
        try:
            del self[event.target][nick]
        except KeyError:
            for i in self[event.target].values():
                if i['host'] == event.source.host:
                    del self[event.target][i['hostmask'].split("!")[0]]
                    break

    def add_entry(self, channel: str, nick: str, hostmask: str, account: str):
        temp: UserDB = {
            'hostmask': hostmask,
            'host': hostmask.split("@")[1],
            'account': account,
            'seen': None
        }

        if channel not in self:
            self[channel] = {}

        if nick in self[channel]:
            del temp['seen']
            self[channel][nick].update(temp)
        else:
            self[channel][nick] = temp

    def get_user_host(self, channel: str, nick: str):
        try:
            host = f"*!*@{self[channel][nick]['host']}"
        except KeyError:
            self.irc.send(f"WHO {channel} nuhs%nhuac")
            host = f"*!*@{self[channel][nick]['host']}"
        return host

    def flush(self):
        with open('userdb.json', 'w') as f:
            # Use dict(self) to onyly get the actual dict object
            # Use copy.deepcopy() to avoid having errors due to the DB being updated while we flush it
            json.dump(copy.deepcopy(dict(self)), f, indent=2, separators=(',', ': '))
            f.write("\n")
