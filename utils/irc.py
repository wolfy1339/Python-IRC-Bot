import re

def normalizeWhitespace(s, removeNewline=True):
    """Normalizes the whitespace in a string; \s+ becomes one space."""
    if not s:
        return str(s)  # not the same reference
    starts_with_space = (s[0] in ' \n\t\r')
    ends_with_space = (s[-1] in ' \n\t\r')
    if removeNewline:
        newline_re = re.compile('[\r\n]+')
        s = ' '.join([i for i in newline_re.split(s) if bool(i)])
    s = ' '.join([i for i in s.split('\t') if bool(i)])
    s = ' '.join([i for i in s.split(' ') if bool(i)])
    if starts_with_space:
        s = ' ' + s
    if ends_with_space:
        s += ' '
    return s


def formatCmdDocs(docs, name):
    doclines = docs.splitlines()
    s = '{0!s} {1!s}'.format(name, doclines.pop(0))
    if doclines:
        doc = ' '.join(doclines)
        s = '({0!s}) -- {1!s}'.format('\x02' + s + '\x0F', doc)
    return normalizeWhitespace(s)


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]


def setMode(irc, channel, users, mode):
    for block in chunks(users, 4):
        modes = "".join(mode[1:]) * len(block)
        irc.mode(channel, " ".join(block), mode[0] + modes)


def getUsersFromCommaList(args):
    pos = args.rfind(",")
    if args[pos + 1] != " ":
        users = args[:pos].strip().split(",")
    else:
        users = args[:pos].strip().split(", ")
    args = args[pos:].strip().split(" ")

    users.append(args[0][1:])
    return users


def getInfoTuple(event, args):
    if args[0].startswith("#"):
        channel = args[0]
        str_args = " ".join(args[1:])
    else:
        channel = event.target
        str_args = " ".join(args)
    if str_args.find(",") != -1:
        users = getUsersFromCommaList(str_args)
    else:
        users = args[-1:]
    if not " ".join(args[:-len(users)]) == '':
        message = " ".join(args[:-len(users)])
    else:
        message = "{0}".format(event.source.nick)
    return channel, users, message
