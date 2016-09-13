import zirc, ssl, socket

class Bot(zirc.Client):
    def __init__(self):
        self.connection = zirc.Socket(family=socket.AF_INET6, wrapper=ssl.wrap_socket)
        self.config = zirc.IRCConfig(host="irc.freenode.net",
            port=6697,
            nickname="wolfyzIRCBot",
            ident="zirc",
            realname="A zIRC bot",
            channels=["##wolfy1339"],
            sasl_user="BigWolfy1339",
        )

        self.connect(self.config)
        self.start()

    def on_privmsg(bot, event, irc):
        irc.reply(event, "It works!")
        #Or alternatively:
        #irc.privmsg(event.target, "It works!")
        
    def on_all(irc, raw):
        print(raw)


Bot()
