import html.parser
import json
import time
import re
from common import *
from datetime import datetime
from time import sleep
RegisterMod(__name__)

# Generic useful functions
def GetTPTSessionInfo(line):
    with open("passwords.txt") as f:
        return f.readlines()[line].strip()

# Functions to get info from TPT
def GetPostInfo(postID):
    page = GetPage("http://tpt.io/Groups/Thread/View.html?Group=832&Thread={0}".format(postID))
    match = re.search(
        "<div class=\"Comment\">(.+?<div id=\"MessageContainer-{0}\" class=\"Message\">.+?)</li>".format(postID),
        page, re.DOTALL)
    matchinfo = filter(None, re.split("[ \n\t]*<.+?>[ \n\t]*", match.group(1)))
    # "[ \n\t]*</?div.+?>[ \n\t+]*"
    print(matchinfo)

def FormatDate(unixtime):
    timestruct = time.localtime(unixtime)
    strftime = time.strftime("%a %b %d %Y %I:%M:%S%p", timestruct)
    return strftime

# Moderation functions
def HidePost(postID, remove, reason):
    data = {"Hide_Reason": reason, "Hide_Hide": "Hide Post"}
    if remove:
        data["Hide_Remove"] = "1"
    GetPage("http://powdertoy.co.uk/Groups/Thread/HidePost.html?Group=832&Post={0}&Key={1}".format(
          postID, GetTPTSessionInfo(1)), GetTPTSessionInfo(0), data)

def UnhidePost(postID):
    GetPage("http://powdertoy.co.uk/Groups/Thread/UnhidePost.html?Group=832&Post={0}&Key={1}".format(
            postID, GetTPTSessionInfo(1)), GetTPTSessionInfo(0))

def LockThread(threadID, reason):
    GetPage("http://powdertoy.co.uk/Groups/Thread/Moderation.html?Group=832&Thread={0}".format(threadID),
            GetTPTSessionInfo(0), {"Moderation_Lock": "Lock Thread", "Moderation_LockReason": reason})

def UnlockThread(threadID):
    GetPage("http://powdertoy.co.uk/Groups/Thread/Moderation.html?Group=832&Thread={0}".format(threadID),
            GetTPTSessionInfo(0), {"Moderation_Unlock": "Unlock"})

@command("post", minArgs=1, admin=True)
def Post(username, hostmask, channel, text, account):
    """(post <post ID>). Gets info on a BMN Thread post. Admin only."""
    GetPostInfo(text[0])

@command("hide", minArgs=1, adminr=True)
def Hide(username, hostmask, channel, text, account):
    """(hide <post ID> [<reason>]). Hides a post in BMN. Admin only."""
    HidePost(text[0], False, " ".join(text[1:]))

@command("unhide", minArgs=1, admin=True)
def Unhide(username, hostmask, channel, text, account):
    """(unhide <post ID>). Unhides a post in BMN. Admin only."""
    UnhidePost(text[0])

@command("lock", minArgs=2, admin=True)
def Lock(username, hostmask, channel, text, account):
    """(lock <thread ID> <reason>). Locks a thread in BMN. Admin only."""
    LockThread(text[0], " ".join(text[1:]))

@command("unlock", minArgs=1, admin=True)
def Unlock(username, hostmask, channel, text, account):
    """(unlock <thread ID>). Unlocks a thread in BMN. Admin only."""
    UnlockThread(text[0])
