import subprocess
from socket import inet_aton
from struct import unpack

import flask
from flask import request

irc = None
bot = None
app = flask.Flask(__name__)


def ip2long(ip_addr):
    return unpack("!L", inet_aton(ip_addr))[0]


@app.route('/', methods=['POST'])
def main():
    iplow = ip2long('192.30.252.0')
    iphigh = ip2long('192.30.255.255')
    if request.remote_addr in range(iplow, iphigh):
        payload = request.json
        if payload["repository"]["name"] == "Python-IRC-Bot":
            try:
                subprocess.check_call(["git", "pull"])
            except subprocess.CalledProcessError:
                irc.privmsg("##wolfy1339", "git pull failed!")
            else:
                if "handlers.py" in payload['head_commit']['modified']:
                    bot.events = __import__("handlers").Events(bot)
                    for h in dir(bot.events):
                        func = getattr(bot.events, h)
                        if callable(func) and not h.startswith("__"):
                            setattr(bot, h, func)
            return flask.Response("Thanks.", mimetype="text/plain")
        return flask.Response("Wrong repo.", mimetype="text/plain")
    else:
        flask.abort(403)
