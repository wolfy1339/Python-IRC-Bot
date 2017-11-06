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
    if ip2long(request.remote_addr) in range(iplow, iphigh):
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


@app.route('/shutdown', methods=['POST'])
def shutdown():
    if ip2long(request.remote_addr) == ip2long("162.252.175.111"):
        payload = request.get_json()
        hashed = '271e2657c81362de2945b197a1e59be650a103d9fdc0109ec4d1a83d96b36d030842d8eb075cc2e15b1305461628fea1'
        if payload['hash'] == hashed:
            shutdown_server()
            return 'Server shutting down...'
    return flask.abort(403)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def ssl_context():
    import ssl, sys
    if tuple(sys.version_info)[:-2] < (2, 7, 13):
        ssl.PROTOCOL_TLS = ssl.PROTOCOL_SSLv23
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain('/etc/ssl/certs/znc.pem')
    return context
