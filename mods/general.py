from common import *
import math
import string
RegisterMod(__name__)

@command("help", minArgs = 1)
def HelpCmd(username, hostmask, channel, text):
    """<command> Shows help for a command."""
    for mod in commands:
        for i in commands[mod]:
            if i[0] == text[0]:
                if i[1].__doc__:
                    SendMessage(channel, "{0}: {1}".format(text[0], i[1].__doc__))
                else:
                    SendMessage(channel, "No help text available for {0}.".format(text[0]))
                return
    SendNotice(username, "No such command")

@command("list")
def ListCmd(username, hostmask, channel, text, account):
    """(no args). Lists all commands."""
    if len(text):
        if not text[0] in commands:
            SendNotice(username, "No such module")
        else:
            SendMessage(channel, "Commands: "+", ".join(i[0] for i in commands[text[0]]))
    else:
        SendMessage(channel, "Modules: "+", ".join(i for i in commands))

@command("commands")
def CommandsCmd(username, hostmask, channel, text):
    """(no args). Lists all commands."""
    cmdlist = []
    for mod in commands:
        cmdlist += commands[mod]
    SendMessage(channel, ", ".join(i[0] for i in cmdlist))

@command("ping")
def PingCmd(username, hostmask, channel, text):
    """PONG"""
    SendMessage(channel, "pong")

@command("join", minArgs = 1, owner = True)
def JoinCmd(username, hostmask, channel, text):
    """(no args). Make the bot join a channel (admin only)."""
    Send("JOIN {0}\n".format(text[0]))

@command("part", minArgs = 1, owner = True)
def PartCmd(username, hostmask, channel, text):
    """(no args). Make the bot part a channel (admin only)."""
    Send("PART {0}\n".format(text[0]))

"""def Parse(raw, text):
    if text[1] == "324":
        SendMessage(channels[2], "Channel exists: "+text[3] + "; " + text[4])
    elif text[1] == "403":
        SendMessage(channels[2], "No such channel: "+text[3])"""

"""@command("check", minArgs = 1)
def PartCmd(username, hostmask, channel, text):
    ""secret command.""
    for i in text:
        Send("MODE {0}\n".format(i))"""

@command("msg", minArgs = 2, owner = True)
def MsgCmd(username, hostmask, channel, text):
    """(msg <channel> <message>). Sends a message to a channel."""
    SendMessage(text[0], " ".join(text[1:]))

@command("raw", minArgs = 1, owner = True)
def MsgCmd(username, hostmask, channel, text):
    """(raw <message>). Sends a raw IRC message."""
    Send(" ".join(text) + "\n")

"""@command("vigenere", minArgs = 2)
def Viginerecmd(username, hostmask, channel, text):
    ""(<string> <listofkeys>...). moo""
    for i in text[1:]:
        (enc, dec) = Viginere(text[0], i)
        SendMessage(channel, "Encrypted: {0}, Decrypted: {1}".format(enc, dec))"""

"""@command("vigenere2", minArgs = 2)
def Viginere2cmd(username, hostmask, channel, text):
    ""(<string> <listofkeys>...). moo""
    checked = []
    for i in text[1:]:
        (enc, dec) = Viginere(text[0], i)
        checked.append(dec)
        Send("MODE ####{0}\n".format(dec))
    SendMessage(channels[2], "Checking: " + ", ".join(checked))

@command("vigenere3", minArgs = 2)
def Viginere3cmd(username, hostmask, channel, text):
    ""(<keys> <listofstrings>...). moo""
    checked = []
    for i in text[1:]:
        (enc, dec) = Viginere(i, text[0])
        checked.append(dec)
        Send("MODE ####{0}\n".format(dec))
    SendMessage(channels[2], "Checking: " + ", ".join(checked))
    
alpha = string.lowercase
def Viginere(incoming, KEY, offset = 1):
    ## subtract 1 so it works with python's 0's index for lists
    ## this part actually broke it, and ended up making it a ROT12
    ## when it should have been a ROT13
    offset -= 1

    ## generate the Vigenere square shading
    chart = dict()
    k = 0
    for letter in alpha:
        if k + offset >= len(alpha):
            ## rotation won't go beyond end of row
            sanit = k + offset - len(alpha)
            chart[letter] = alpha[sanit:] + alpha[:sanit]
        else:
            ## rotation goes beyond the end of the row
            chart[letter] = alpha[k + offset:] + alpha[:k + offset]
        k += 1

    ## display the chart to stdout
    ordered_rows = chart.keys()
    ordered_rows.sort()
    #for x in ordered_rows:
    #    print x, chart[x]
    #print ''

    ## pad the key with the length of the incoming text
    multi = math.ceil(len(incoming) / float(len(KEY)))
    long_key = KEY * int(multi)


    ## encrypted the incoming text
    j = 0
    output_encrypted = str()
    for x in incoming:
        y = x.lower()
        if y in chart:
            row = chart[y]
            idx = (string.lowercase).find(long_key[j].lower())
            output_encrypted += chart[y][idx]
            j += 1
        else:
            output_encrypted += y

    ## decrypt the incoming text
    p = 0
    output_decrypted = str()
    for x in incoming:
        y = x.lower()
        stop = False
        before = len(output_decrypted)
        for letter in chart:
            row = chart[letter]
            if not stop and y in chart:
                idx = (string.lowercase).find(long_key[p].lower())
                if row[idx] == y:
                    output_decrypted += letter
                    p += 1
                    stop = True
        after = len(output_decrypted)
        if before == after:
            output_decrypted += y

        return (output_encrypted.upper(), output_decrypted.upper())
    #SendMessage(channels[2], "Encrypted: {0}, Decrypted: {1}".format(output_encrypted.upper(), output_decrypted.upper()))
    #print 'Encrypted:', output_encrypted.upper()
    #print 'Decrypted:', output_decrypted.upper()"""
