import sys
try:
  import urllib.request
  import urllib.parse
  import urllib.error
except ImportError:
    import urllib, urllib2
import re
from config import *

def CheckOwner(hostmask):
    host = hostmask.split("!")[-1]
    return host in ownerHostmasks

def CheckAdmin(hostmask):
    host = hostmask.split("!")[-1]
    return host in adminHostmasks or CheckOwner(hostmask)

#only used for stocks.py, maybe for more later
logins = {}
def GetAccount(hostmask):
    return logins[hostmask] if hostmask in logins else None

messageQueue = []
def Send(msg):
    messageQueue.append(msg)

def SendMessage(target, msg):
    msg = msg[:450]
    if re.match(".*moo+$", msg):
        msg = msg + "."
    Send("PRIVMSG {0} :{1}\n".format(target, msg))

def SendNotice(target, msg):
    msg = msg[:450]
    Send("NOTICE {0} :{1}\n".format(target, msg))

plugin = ""
def RegisterMod(name):
    global plugin
    commands[name] = []
    plugin = name

commands = {}
def command(name, minArgs = 0, needsAccount = False, owner = False, admin = False):
    def real_command(func):
        def call_func(username, hostmask, channel, text):
            if owner and not CheckOwner(hostmask):
                SendNotice(username, "This command is owner only")
                return
            if admin and not CheckAdmin(hostmask):
                SendNotice(username, "This command is admin only")
                return
            if len(text) < minArgs:
                SendNotice(username, "Usage: {0}".format(func.__doc__))
                return
            account = GetAccount(hostmask)
            if needsAccount and not account:
                SendNotice(username, "You are not logged in")
                return
            return func(username, hostmask, channel, text, account)
        call_func.__doc__ = func.__doc__
        commands[plugin].append((name, call_func))
        return call_func
    return real_command

def GetPage(url, cookies = None, headers = None, removeTags = False, getredirect=False):
    try:
        if cookies:
            if sys.version_info[0] > 2:
                req = urllib.request.Request(url, data=urllib.parse.urlencode(headers).encode("utf-8") if headers else None, headers={'Cookie':cookies.encode("utf-8")})
            else:
                req = urllib2.Request(url, data=urllib.urlencode(headers).encode("utf-8") if headers else None, headers={'Cookie':cookies.encode("utf-8")})
        else:
            if sys.version_info[0] > 2:
                req = urllib.request.Request(url, data=urllib.parse.urlencode(headers).encode("utf-8") if headers else None)
            else:
                req = urllib2.Request(url, data=urllib.urlencode(headers).encode("utf-8") if headers else None)
        if sys.version_info[0] > 2:
            data = urllib.request.urlopen(req, timeout=10)
        else:
            data = urllib2.urlopen(req, timeout=10)
        page = data.read().decode("utf-8", errors="replace")
        url = data.geturl()
        if removeTags:
            return re.sub("<.*?>", "", page)
        return url if getredirect else page
    except urllib.error.URLError:
    #except IOError:
        return None
