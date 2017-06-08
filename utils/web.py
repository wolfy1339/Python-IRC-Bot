import subprocess
from socket import inet_aton
from struct import unpack

import flask
from flask import request
from .util import reload_handlers

def ip2long(ip_addr):
    return unpack("!L", inet_aton(ip_addr))[0]

app = flask.Flask(__name__)
class HTTPServer(object):
    def __init__(self, bot):
        self.privmsg = bot.privmsg
        self.bot = bot
        self.main = app.route('/', methods=['POST'])(self.main)

    def main():
        iplow = ip2long('192.30.252.0')
        iphigh = ip2long('192.30.255.255')
        if request.remote_addr in range(iplow, iphigh):
            payload = request.get_json()
            if payload["repository"]["name"] == "Python-IRC-Bot":
                try:
                    subprocess.check_call(["git", "pull"])
                except subprocess.CalledProcessError:
                    self.privmsg("##wolfy1339", "git pull failed!")
                else:
                    if "handlers.py" in payload['head_commit']['modified']:
                        reload_handlers(self.bot)
                return flask.Response("Thanks.", mimetype="text/plain")
            return flask.Response("Wrong repo.", mimetype="text/plain")
        else:
            flask.abort(403)
