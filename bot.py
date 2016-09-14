import zirc
import ssl
import socket
import os
import math


class Bot(zirc.Client):
    def __init__(self):
        self.connection = zirc.Socket(family=socket.AF_INET6,
                                      wrapper=ssl.wrap_socket)
        self.config = zirc.IRCConfig(host="irc.freenode.net",
                                     port=6697,
                                     nickname="wolfyzIRCBot",
                                     ident="zirc",
                                     realname="A zIRC bot",
                                     channels=["##wolfy1339"],
                                     sasl_user="BigWolfy1339",
                                     sasl_pass="")

        self.connect(self.config)
        self.start()

    def on_ctcp(irc, raw):
        print(raw)
    def on_privmsg(self, event, irc):
        privmsg = event.target == self.config['nickname']
        target = "a private message" if privmsg else event.target
        arguments = " ".join(event.arguments)
        if arguments.startswith("?help"):
            args = arguments.split("?help")[1].strip()
            if args == "quit" or args == "?quit":
                irc.reply(event, "(\x02quit <text>\x0F) -- Exits the bot with the QUIT message <text>.")
            elif args == "echo" or args == "?echo":
                irc.reply(event, "(\x02echo <text>\x0F) -- Returns the arguments given.")
            else:
                irc.reply(event, "Invalid command {}".format(arguments.split("?help")[1].strip()))
        elif arguments.startswith("?quit"):
            print("{} called quit in {}".format(event.source.nick, target))
            irc.quit(arguments.split("?quit")[1].strip())
            os._exit(1)
        elif arguments.startswith("?ping"):
            print("{} called ping in {}".format(event.source.nick, target))
            irc.reply(event, "PONG!")
        elif arguments.startswith("?join"):
            print("{} called join in {}".format(event.source.nick, target))
            irc.join(arguments.split("?join")[1].strip())
        elif arguments.startswith("?part"):
            print("{} called part in {}".format(event.source.nick, target))
            irc.part(arguments.split("?join")[1].strip())
        elif arguments.startswith("?ban"):
            irc.ban(event.target, arguments.split("?ban")[1].strip())
        elif arguments.startswith("?unban"):
            irc.unban(event.target, arguments.split("?unban")[1].strip())
        elif arguments.startswith("?op"):
            irc.op(event.target, arguments.split("?unban")[1].strip())
        elif arguments.startswith("?deop"):
            irc.deop(event.target, arguments.split("?unban")[1].strip())
        elif arguments.startswith("?voice"):
            irc.voice(event.target, arguments.split("?voice")[1].strip())
        elif arguments.startswith("?unvoice"):
            irc.unvoice(event.target, arguments.split("?voice")[1].strip())
        elif arguments.startswith("?echo"):
            irc.reply(event, arguments.split("?echo")[1].strip())
        elif arguments.startswith("?calc"):
            safe_dict = {
                "sqrt": math.sqrt,
                "pow": math.pow,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "asin": math.asin,
                "acos": math.acos,
                "atan": math.atan,
                "abs": abs,
                "log": math.log,
                "fact": math.factorial,
                "factorial": math.factorial
            }

            try:
                t = arguments.split("?calc")[1].strip()
                t = t.replace("pi", math.pi)
                t = t.replace("e", math.e)
                a = format(eval(t, {"__builtins__": None}, safe_dict), ",d")
                irc.reply(event, "The answer is: {0}".format(a))
            except ArithmeticError:
                irc.reply(event, "\x034Number undefined or too large.")
            except Exception:
                irc.reply(event, "\x034Invalid Input")
        elif arguments.startswith("?"):
            irc.reply(event, "Invalid command {}".format(arguments.strip()))
        print(event.raw)


Bot()
