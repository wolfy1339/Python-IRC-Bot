# STD lib imports
import sys
import time
# Pacakge imports
import config
import log
import plugins
import hooks  # pylint: disable=unused-import
from utils import irc as irc_utils
from utils import util, web
# Third-party imports
import iso8601 as iso


class Actions(object):
    @staticmethod
    def on_ctcp(irc, event, raw):
        log.info("Received CTCP reply " + raw)

    def on_privmsg(self, event, irc, arguments):
        str_args = " ".join(arguments)
        nickname = self.config['nickname']
        if (str_args.startswith(config.commandChar) or
                str_args.split(" ")[0][:-1] == nickname):
            util.call_command(self.bot, event, irc, arguments)
        else:
            util.call_hook(self.bot, event, irc, arguments)
        nick = event.source.nick
        str_args = ' '.join(arguments)
        regex = r"^u[/]([^/]+)[/]([^/]+)[/]([^/]+)[/]?$|^s[/]([^/]+)[/]([^/]+)[/]?$"
        if __import__("re").match(regex, str_args) is None:
            self._update_seen_db(event, irc, nick, str_args)

    @staticmethod
    def _get_time(tags):
        if len(tags):
            try:
                timeTag = [tag for tag in tags if hasattr(tag, time)][0]
                date = iso.parse_date(timeTag)
                timestamp = time.mktime(date.timetuple())
            except Exception:
                timestamp = time.time()
        else:
            timestamp = time.time()
        return timestamp

    def _update_seen_db(self, event, irc, nick, str_args):
        timestamp = self._get_time(event.tags)
        try:
            udb = self.userdb[event.target][nick]
            if udb['seen'] is None:
                udb['seen'] = []
            msg = irc_utils.strip_colours(str_args)
            udb["seen"].append({'time': timestamp, 'message': msg})

            def compare(m):
                return m["time"]
            self.userdb[event.target][nick]['seen'] = sorted(udb["seen"],
                                                             key=compare)[-5:]
        except KeyError:
            irc.send(f"WHO {event.target} nuhs%nhuac")

    @staticmethod
    def on_send(data):
        if data.find("%") == -1:
            log.debug(data)

    def on_nick(self, event, irc):
        nick = event.source.nick
        to_nick = event.arguments[0]
        for chan in self.userdb:
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
            web.app.stop()
            self.bot.web.stop()
            self.userdb.flush()
            self.bot.db_job.stop()
            sys.exit(1)
        else:
            for chan in self.userdb:
                try:
                    del self.userdb[chan][nick]
                    break
                except KeyError:
                    chandb = self.userdb[chan]
                    for u in chandb:
                        if chandb[u]['host'] == event.source.host and u == nick:
                            del self.userdb[chan][u]
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
                log.warning(
                    "Removed from %s, trying to re-join", event.target)
                irc.join(event.target)
            else:
                del self.userdb[event.target]
        else:
            self.userdb.remove_entry(event, nick)

    def on_join(self, event, irc):
        args = event.arguments
        if event.source.nick == self.config['nickname']:
            log.info("Joining %s", event.target)
            if event.target not in self.userdb:
                self.userdb[event.target] = {}
            irc.send(f"WHO {event.target} nuhs%nhuac")
            irc.send(f"NAMES {event.target}")
        else:
            # Extended join methods
            if len(args):
                nick = event.source.nick
                hostmask = event.source
                channel = event.target
                account = args[0] if args[0] != "*" else None
                self.userdb.add_entry(channel, nick, hostmask, account)
            irc.send(f"WHO {event.source.nick} nuhs%nhuac")

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
                log.info("Received channel notice from %s in %s",
                         source,
                         channel)
            else:
                log.info("Received private notice from %s", source)
