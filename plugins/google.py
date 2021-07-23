from utils import util

@add_cmd("google", min_args=1)
def search(bot, irc, event, args):
    pass
    r = util.get("https://google.com/search" params={"q": " ".join(args)})
    return r.text


@add_cmd("translate", min_args=1)
def translate(bot, irc, event, args):
    pass
