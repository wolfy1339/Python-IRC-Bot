import subprocess
from socket import inet_aton
from struct import unpack

import flask
from flask import request
from .util import reload_handlers

irc = None
bot = None
app = flask.Flask(__name__)
app.debug = False


def ip2long(ip_addr):
    return unpack("!L", inet_aton(ip_addr))[0]


@app.route('/', methods=['POST'])
def main():
    iplow = ip2long('192.30.252.0')
    iphigh = ip2long('192.30.255.255')
    if request.remote_addr in range(iplow, iphigh):
        payload = request.get_json()
        if payload["repository"]["name"] == "Python-IRC-Bot":
            try:
                subprocess.check_call(["git", "pull"])
            except subprocess.CalledProcessError:
                irc.privmsg("##wolfy1339", "git pull failed!")
            else:
                if "handlers.py" in payload['head_commit']['modified']:
                    reload_handlers(bot)
            return flask.Response("Thanks.", mimetype="text/plain")
        return flask.Response("Wrong repo.", mimetype="text/plain")
    else:
        flask.abort(403)


def ssl_context():
    import ssl, sys
    if tuple(sys.version_info)[:-2] < (2, 7, 13):
        ssl.PROTOCOL_TLS = ssl.PROTOCOL_SSLv23
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain('/etc/ssl/certs/znc.pem')
    return context
