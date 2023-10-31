#!/usr/bin/python3
from time import sleep
from builtins import bytes as bbytes
import re, random as r, codecs
from sys import argv as args
from socket import socket, AF_INET, SOCK_STREAM
from os import environ as env
from dotenv import load_dotenv

load_dotenv()


class bytes(bbytes):
    """Local override of builtin bytes class to add "lazy_decode\" """

    def lazy_decode(e):
        return str(e)[2:-1]


__version__ = "v1.0.5"
ircsock = socket(AF_INET, SOCK_STREAM)
botnick = "FireBot"
servers = {
    "ircnow": {
        "address": "localhost",
        "port": 6601,
        "interval": 200,
        "pass": env["ircnow_pass"],
        "channels": {"#random": 0, "#dice": 0, "#offtopic": 0, botnick: 0},
        "admins": ["firepup", "h|thelounge"],
    },
    "efnet": {
        "address": "irc.servercentral.net",
        "channels": {"#random": 0, "#dice": 0, botnick: 0},
        "admins": ["firepup", "h|tl"],
    },
    "replirc": {
        "address": "localhost",
        "pass": env["replirc_pass"],
        "channels": {"#random": 0, "#dice": 0, "#main": 0, "#bots": 0, botnick: 0},
        "admins": ["firepup", "firepup|lounge", "h|tl"],
    },
}
gmode = False
server = args[1]
nicklen = 30
address = servers[server]["address"]
port = servers[server]["port"] if "port" in servers[server] else 6667
channels = servers[server]["channels"]
interval = servers[server]["interval"] if "interval" in servers[server] else 50
encoding = "UTF-8"
prefix = "."
rebt = "fire"
gblrebt = "all"
lrebt = 7 + len(rebt)
lgblrebt = 7 + len(gblrebt)
e = encoding
adminnames = servers[server]["admins"]
exitcode = f"bye {botnick.lower()}"
ircmsg = ""
blanks = 0
npbase = "\[\x0303last\.fm\x03\] [A-Za-z0-9_[\]{}\\|^]{1,MAX} (is listening|last listened) to: \x02.+ - .+\x02 \([0-9]+ plays\)( \[.*\])?"
np = re.compile(
    npbase.replace("MAX", f"{nicklen}")
)
npallowed = ["FireBitBot"]
ESCAPE_SEQUENCE_RE = re.compile(
    r"""
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )""",
    re.UNICODE | re.VERBOSE,
)


def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), "unicode-escape")

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


def sucheck(message):
    return re.search("^(su|sudo|(su .*|sudo .*))$", message)


def ping(ircmsg):
    pong = f"PONG :{ircmsg.split('PING :')[1]}\n"
    ircsock.send(bytes(pong, e))
    print(pong, end="")


def sendmsg(msg, target):
    if target != "NickServ" and not mfind(msg, ["IDENTIFY"], False):
        print(
            f"[LOG][{server}] Sending {bytes(msg.encode()).lazy_decode()} to {target}"
        )
    else:
        print(f"[LOG][{server}] Identifying myself...")
    ircsock.send(bytes(f"PRIVMSG {target} :{msg}\n", e))


def notice(msg, target, silent: bool = False):
    if not silent:
        print(
            f"[LOG][{server}] Sending {bytes(msg.encode()).lazy_decode()} to {target} (NOTICE)"
        )
    ircsock.send(bytes(f"NOTICE {target} :{msg}\n", e))


def CTCPHandler(msg: str, sender: str = "", isRaw: bool = False):
    if isRaw:
        sender = msg.split("!", 1)[0][1:]
        message = msg.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
    CTCP = msg.split("\x01")[1]
    print(f"[LOG][{server}] Responding to CTCP {CTCP} from {sender}")
    if CTCP == "VERSION":
        notice(
            f"\x01VERSION FireBot {__version__} (https://git.amcforum.wiki/Firepup650/fire-ircbot)\x01",
            sender,
            True,
        )
        return True
    elif CTCP == "USERINFO":
        notice("\x01USERINFO FireBot (Firepup's bot)\x01", sender, True)
        return True
    elif CTCP == "SOURCE":
        notice(
            "\x01SOURCE https://git.amcforum.wiki/Firepup650/fire-ircbot\x01",
            sender,
            True,
        )
        return True
    elif CTCP == "FINGER":
        notice(f"\x01FINGER Firepup's bot\x01", sender, True)
        return True
    elif CTCP == "CLIENTINFO":
        notice(f"\x01CLIENTINFO ACTION VERSION USERINFO SOURCE FINGER", sender, True)
        return True
    return False


def joinserver():
    print(f"[LOG][{server}] Joining {server}...")
    global e, nicklen, npbase, np, botnick
    ircsock.connect((address, port))
    ircsock.send(bytes(f"USER {botnick} {botnick} {botnick} {botnick}\n", e))
    ircsock.send(bytes(f"NICK {botnick}\n", e))
    ircmsg = ""
    while (
        ircmsg.find("MODE " + botnick) == -1 and ircmsg.find("PRIVMSG " + botnick) == -1
    ):
        ircmsg = ircsock.recv(2048).strip(b"\r\n").decode()
        if ircmsg != "":
            print(bytes(ircmsg.encode()).lazy_decode())
            if ircmsg.find("NICKLEN=") != -1:
                global nicklen
                nicklen = int(ircmsg.split("NICKLEN=")[1].split(" ")[0])
                np = re.compile(
                    npbase.replace("MAX", f"{nicklen}")
                )
                print(f"[LOG][{server}] NICKLEN set to {nicklen}")
            if ircmsg.find("Nickname already in use") != -1:
                print(f"[LOG][{server}] My nickname's in use? lemme try that again...")
                botnick = f"{botnick}{r.randint(0,1000)}"
                ircsock.send(bytes(f"NICK {botnick}\n", e))
                print(f"[LOG][{server}] botnick is now {botnick}")
            if ircmsg.find("PING :") != -1:
                # pong = "PONG :" + input("Ping?:") + "\n"
                # pong = pong.replace("\\\\", "\\")
                ping(ircmsg)
            if len(ircmsg.split("\x01")) == 3:
                CTCPHandler(ircmsg, isRaw=True)
            if ircmsg.find("Closing Link") != -1:
                print(f"[LOG][{server}] I tried.")
                exit(f"[EXIT][{server}] Closing Link")
    print(f"[LOG][{server}] Joined {server} successfully!")


def mfind(message: str, find: list, usePrefix: bool = True):
    if usePrefix:
        return any(message[: len(match) + 1] == prefix + match for match in find)
    else:
        return any(message[: len(match)] == match for match in find)


def joinchan(chan: str, origin: str, chanList: dict, lock: bool = True):
    print(f"[LOG][{server}] Joining {chan}...")
    chan = chan.replace(" ", "")
    if "," in chan:
        chans = chan.split(",")
        for subchan in chans:
            chanList = joinchan(subchan, origin, chanList)
        return chanList
    if chan.startswith("0"):
        if origin != "null":
            sendmsg("Refusing to join channel 0", origin)
        return chanList
    if chan in channels and lock:
        if origin != "null":
            sendmsg(f"I'm already in {chan}.", origin)
        return chanList
    ircsock.send(bytes(f"JOIN {chan}\n", e))
    ircmsg = ""
    while True:
        ircmsg = ircsock.recv(2048).strip(b"\r\n").decode()
        if ircmsg != "":
            print(bytes(ircmsg.encode()).lazy_decode())
            if ircmsg.find("PING :") != -1:
                ping()
            if len(ircmsg.split("\x01")) == 3:
                CTCPHandler(ircmsg, isRaw=True)
        if ircmsg.find("No such channel") != -1:
            print(f"[LOG][{server}] Joining {chan} failed (DM)")
            if origin != "null":
                sendmsg(f"{chan} is an invalid channel", origin)
            break
        elif ircmsg.find("Cannot join channel (+i)") != -1:
            print(f"[LOG][{server}] Joining {chan} failed (Private)")
            if origin != "null":
                sendmsg(f"Permission denied to channel {chan}", origin)
            break
        elif ircmsg.find("End of") != -1:
            print(f"[LOG][{server}] Joining {chan} succeeded")
            if origin != "null":
                sendmsg(f"Joined {chan}", origin)
            chanList[chan] = 0
            break
    return chanList


def op(name, chan):
    if name != "":
        print(f"[LOG][{server}] Attempting op of {name}...")
        ircsock.send(bytes(f"MODE {chan} +o {name}\n", e))


def main():
    try:
        global ircmsg, channels, e, gmode, prefix, rebt, gblrebt, lrebt, lgblrebt, blanks
        print(f"[LOG][{server}] Starting connection..")
        joinserver()
        if "pass" in servers[server]:
            sendmsg(f"IDENTIFY FireBot {servers[server]['pass']}", "NickServ")
            sleep(0.5)
        for chan in channels:
            joinchan(chan, "null", channels, False)
        while 1:
            global ircmsg, gmode
            raw = bytes(ircsock.recv(2048).strip(b"\r\n"))
            ircmsg = raw.decode()
            if ircmsg == "":
                exit(f"[EXIT][{server}] Probably a netsplit")
            else:
                print(raw.lazy_decode(), sep="\n")
                if ircmsg.find("PRIVMSG") != -1:
                    # Format of ":[Nick]!~[hostname]@[IP Address] PRIVMSG [channel] :[message]”
                    name = ircmsg.split("!", 1)[0][1:]
                    helpErr = False
                    if (name.startswith("saxjax") and server == "efnet") or (
                        name == "ReplIRC" and server == "replirc"
                    ):
                        if ircmsg.find("<") != -1 and ircmsg.find(">") != -1:
                            Nname = ircmsg.split("<", 1)[1].split(">", 1)[0].strip()
                            if name == "ReplIRC":
                                name = Nname[4:]
                            else:
                                name = Nname
                            message = ircmsg.split(">", 1)[1].strip()
                            helpErr = True
                        else:
                            message = (
                                ircmsg.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
                            )
                    else:
                        message = ircmsg.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
                    if name.endswith("dsc"):
                        helpErr = True
                    chan = ircmsg.split("PRIVMSG", 1)[1].split(":", 1)[0].strip()
                    print(
                        f'[LOG][{server}] Got "{bytes(message.encode()).lazy_decode()}" from "{name}" in "{chan}"'
                    )
                    if "goat" in name.lower() and gmode == True:
                        print(f"[LOG][{server}] GOAT DETECTED")
                        sendmsg("Hello Goat", chan)
                        gmode = False
                    if len(name) < nicklen and chan in channels:
                        channels[chan] += 1
                    elif len(name) > nicklen:
                        print(
                            f"[LOG][{server}] Name too long ({len(name)} > {nicklen})"
                        )
                        continue
                    elif chan not in channels:
                        print(
                            f"[LOG][{server}] Channel not in channels ({chan} not in {channels})"
                        )
                        continue
                    if mfind(
                        message.lower(),
                        [f"hi {botnick.lower()}", f"hello {botnick.lower()}"],
                        False,
                    ):
                        sendmsg(f"Hello {name}!", chan)
                    elif (
                        mfind(message, ["op me"], False) and name.lower() in adminnames
                    ):
                        op(name, chan)
                    elif mfind(message, ["amIAdmin"]):
                        sendmsg(
                            f"{name.lower()} in {adminnames} == {name.lower() in adminnames}",
                            chan,
                        )
                    elif mfind(message, ["help"]):
                        if not helpErr:
                            sendmsg("List of commands:", name)
                            sendmsg(f'Current prefix is "{prefix}"', name)
                            sendmsg(f"{prefix}help - Sends this help list", name)
                            sendmsg(
                                f"{prefix}quote - Sends a random firepup quote", name
                            )
                            sendmsg(
                                f"{prefix}(eightball,8ball,8b) [question]? - Asks the magic eightball a question",
                                name,
                            )
                            sendmsg(
                                f"(hi,hello) {botnick} - The bot says hi to you", name
                            )
                            if name.lower() in adminnames:
                                sendmsg(f"reboot {rebt} - Restarts the bot", name)
                                sendmsg(exitcode + " - Shuts down the bot", name)
                                sendmsg("op me - Makes the bot try to op you", name)
                                sendmsg(
                                    f"{prefix}join [channel(s)] - Joins the bot to the specified channel(s)",
                                    name,
                                )
                        else:
                            sendmsg("Sorry, I can't send help to bridged users.", chan)
                    elif name.lower() in adminnames and mfind(
                        message, ["goat.mode.activate"]
                    ):
                        print(f"[LOG][{server}] GOAT DETECTION ACTIVATED")
                        gmode = True
                    elif name.lower() in adminnames and mfind(
                        message, ["goat.mode.deactivate"]
                    ):
                        print(f"[LOG][{server}] GOAT DETECTION DEACTIVATED")
                        gmode = False
                    elif mfind(message, ["quote"]):
                        r.seed()
                        log = open("mastermessages.txt", "r")
                        q = log.readlines()
                        sel = decode_escapes(
                            str(r.sample(q, 1))
                            .strip("[]'")
                            .replace("\\n", "")
                            .strip('"')
                        )
                        sendmsg(sel, chan)
                        log.close()
                    elif mfind(message, ["join "]) and name.lower() in adminnames:
                        newchan = message.split(" ")[1].strip()
                        channels = joinchan(newchan, chan, channels)
                    elif mfind(message, ["eightball", "8ball", "8b"]):
                        if message.endswith("?"):
                            log = open("eightball.txt", "r")
                            q = log.readlines()
                            sel = (
                                str(r.sample(q, 1))
                                .strip("[]'")
                                .replace("\\n", "")
                                .strip('"')
                            )
                            sendmsg(f"The magic eightball says: {sel}", chan)
                            log.close()
                        else:
                            sendmsg("Please pose a Yes or No question.", chan)
                    elif (
                        mfind(message, ["debug", "dbg"]) and name.lower() in adminnames
                    ):
                        sendmsg(f"[DEBUG] NICKLEN={nicklen}", chan)
                        sendmsg(f"[DEBUG] ADMINS={adminnames}", chan)
                        sendmsg(f"[DEBUG] CHANNELS={channels}", chan)
                    elif (
                        mfind(message, [f"reboot {rebt}", f"reboot {gblrebt}"], False)
                        and name.lower() in adminnames
                    ):
                        for i in channels:
                            sendmsg("Rebooting...", i)
                        ircsock.send(bytes("QUIT :Rebooting\n", e))
                        __import__("os").system(f"python3 -u ircbot.py {server}")
                        exit(f"[EXIT][{server}] Inner layer exited or crashed")
                    elif (
                        name.lower() in adminnames
                        and message.rstrip().lower() == exitcode
                    ):
                        sendmsg("oh...okay. :'(", chan)
                        for i in channels:
                            # print(f'[LOG][{server}] i="{i}" vs chan="{chan}"')
                            if i != chan.strip():
                                sendmsg("goodbye... :'(", i)
                        ircsock.send(bytes("QUIT :Shutting down\n", "UTF-8"))
                        print(f"[LOG][{server}] QUIT")
                        exit(f"[EXIT][{server}] goodbye :'(")
                        # raise EOFError
                    elif sucheck(message):
                        if name.lower() in adminnames:
                            sendmsg(
                                "Error - system failure, contact system operator", chan
                            )
                        elif "bot" in name.lower():
                            print(f"[LOG][{server}] lol, no.")
                        else:
                            sendmsg("Access Denied", chan)
                    elif np.search(message) and name in npallowed:
                        x02 = "\x02"
                        sendmsg(
                            f"f.sp {message.split(':')[1].split('(')[0].strip(f' {x02}')}",
                            chan,
                        )
                    elif len(message.split("\x01")) == 3:
                        if not CTCPHandler(message, name):
                            CTCP = message.split("\x01")[1]
                            if CTCP == "ACTION ducks":
                                sendmsg("\x01ACTION gets hit by a duck\x01", chan)
                            elif CTCP.startswith("ACTION ducks"):
                                sendmsg(
                                    f"\x01ACTION gets hit by {CTCP.split(' ', 2)[2]}\x01",
                                    chan,
                                )
                    if chan in channels and channels[chan] >= interval:
                        r.seed()
                        channels[chan] = 0
                        log = open("mastermessages.txt", "r")
                        q = log.readlines()
                        sel = decode_escapes(
                            str(r.sample(q, 1))
                            .strip("[]'")
                            .replace("\\n", "")
                            .strip('"')
                        )
                        sendmsg(f"[QUOTE] {sel}", chan)
                        log.close()
                else:
                    if ircmsg.find("PING") != -1:
                        ping(ircmsg)
                    if ircmsg.find("Closing Link") != -1:
                        exit(f"[EXIT][{server}] I got killed :'(")
                    if ircmsg.find("ERROR :Ping timeout: ") != -1:
                        exit(f"[EXIT][{server} Ping timeout]")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
