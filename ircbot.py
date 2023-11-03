#!/usr/bin/python3
from time import sleep
from builtins import bytes as bbytes
import re, random as r, codecs
from sys import argv as args, exit as xit
from socket import socket, AF_INET, SOCK_STREAM
from os import environ as env
from dotenv import load_dotenv
from pythonlangutil.overload import Overload, signature
from typing import Iterable, Type, TypeVar, Any
from datetime import datetime as dt

_T = TypeVar("_T")
load_dotenv()


class bytes(bbytes):
    """Local override of builtin bytes class to add "lazy_decode\" """
    self = b''

    def __new__(cls: Type[_T], thing: Any = None, encoding: str = "UTF-8", errors: str="strict") -> _T:
        if type(thing) == str:
            cls.self = super().__new__(cls, thing, encoding, errors)
            return cls.self
        elif thing == None:
            cls.self = super().__new__(cls)
            return cls.self
        else:
            cls.self = super().__new__(cls, thing)
            return cls.self

    @classmethod
    def lazy_decode(cls):
        return str(cls.self)[2:-1]

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
        "address": "irc.mzima.net",
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
server = ""

def log(message: str, origin: str = "serv", time: dt = dt.now(), level: str = "LOG") -> None:
    if origin == "serv":
        origin = args[1]
    print(f"[{level}][{origin}][{time}] {message}")

def exit(message: object) -> None:
    log(message, level = "EXIT")
    xit(1)

if __name__ == "__main__":
    gmode = False
    server = args[1]
    nicklen = 30
    address = servers[server]["address"]
    port = servers[server]["port"] if "port" in servers[server] else 6667
    channels = servers[server]["channels"]
    interval = servers[server]["interval"] if "interval" in servers[server] else 50
    prefix = "."
    rebt = "fire"
    gblrebt = "all"
    lrebt = 7 + len(rebt)
    lgblrebt = 7 + len(gblrebt)
    adminnames = servers[server]["admins"]
    exitcode = f"bye {botnick.lower()}"
    ircmsg = ""
    blanks = 0
    npbase = "\[\x0303last\.fm\x03\] [A-Za-z0-9_[\]{}\\|^]{1,MAX} (is listening|last listened) to: \x02.+ - .+\x02 \([0-9]+ plays\)( \[.*\])?"
    np = re.compile(
        npbase.replace("MAX", f"{nicklen}")
    )
    queue = []
    log(f"Start init for {server}")
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

def decode_escapes(s: str) -> str:
    def decode_match(match):
        return codecs.decode(match.group(0), "unicode-escape")

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


def sucheck(message: str):
    return re.search("^(su|sudo|(su .*|sudo .*))$", message)


def send(command: str, encoding: str = "UTF-8") -> int:
    return ircsock.send(bytes(command))


def recv() -> bytes:
    global queue
    if queue:
        return bytes(queue.pop(0))
    data = bytes(ircsock.recv(2048).strip(b"\r\n"))
    if b'\r\n' in data:
        queue.extend(data.split(b'\r\n'))
        return bytes(queue.pop(0))
    return data


def ping(ircmsg: str) -> int:
    pong = f"PONG :{ircmsg.split('PING :')[1]}\n"
    print(pong, end="")
    return send(pong)


def sendraw(command: str) -> int:
    log(f"RAW sending {command}")
    command = f"{command}\n"
    return send(command.replace("$BOTNICK", botnick))


def sendmsg(msg: str, target: str) -> None:
    if target != "NickServ" and not mfind(msg, ["IDENTIFY"], False):
        log(f"Sending {bytes(msg).lazy_decode()} to {target}")
    else:
        log("Identifying myself...")
    send(f"PRIVMSG {target} :{msg}\n")


def notice(msg, target, silent: bool = False):
    if not silent:
        log(f"Sending {bytes(msg).lazy_decode()} to {target} (NOTICE)")
    send(f"NOTICE {target} :{msg}\n")


def CTCPHandler(msg: str, sender: str = "", isRaw: bool = False):
    if isRaw:
        sender = msg.split("!", 1)[0][1:]
        message = msg.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
    CTCP = msg.split("\x01")[1]
    log(f"Responding to CTCP {CTCP} from {sender}")
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
    log(f"Unknown CTCP {CTCP}")
    return False


def joinserver():
    log(f"Joining {server}...")
    global e, nicklen, npbase, np, botnick
    ircsock.connect((address, port))
    send(f"USER {botnick} {botnick} {botnick} {botnick}\n")
    send(f"NICK {botnick}\n")
    ircmsg = ""
    while (
        ircmsg.find("MODE " + botnick) == -1 and ircmsg.find("PRIVMSG " + botnick) == -1
    ):
        ircmsg = recv().decode()
        if ircmsg != "":
            print(bytes(ircmsg).lazy_decode())
            if ircmsg.find("NICKLEN=") != -1:
                global nicklen
                nicklen = int(ircmsg.split("NICKLEN=")[1].split(" ")[0])
                np = re.compile(
                    npbase.replace("MAX", f"{nicklen}")
                )
                log(f"NICKLEN set to {nicklen}")
            if ircmsg.find("Nickname") != -1:
                log(f"My nickname's in use? lemme try that again...", level = "WARN")
                botnick = f"{botnick}{r.randint(0,1000)}"
                send(f"NICK {botnick}\n")
                log(f"botnick is now {botnick}")
            if ircmsg.startswith("PING "):
                # pong = "PONG :" + input("Ping?:") + "\n"
                # pong = pong.replace("\\\\", "\\")
                ping(ircmsg)
            if len(ircmsg.split("\x01")) == 3:
                CTCPHandler(ircmsg, isRaw=True)
            if ircmsg.find("Closing Link") != -1:
                log("I tried.", level = "EXIT")
                exit("Closing Link")
    log(f"Joined {server} successfully!")


def mfind(message: str, find: list, usePrefix: bool = True):
    if usePrefix:
        return any(message[: len(match) + 1] == prefix + match for match in find)
    else:
        return any(message[: len(match)] == match for match in find)


def joinchan(chan: str, origin: str, chanList: dict, lock: bool = True):
    log(f"Joining {chan}...")
    chan = chan.replace(" ", "")
    if "," in chan:
        chans = chan.split(",")
        for subchan in chans:
            chanList = joinchan(subchan, origin, chanList)
        return chanList
    if chan.startswith("0") or (chan == "#main" and lock):
        if origin != "null":
            sendmsg("Refusing to join channel 0", origin)
        return chanList
    if chan in channels and lock:
        if origin != "null":
            sendmsg(f"I'm already in {chan}.", origin)
        return chanList
    send(f"JOIN {chan}\n")
    ircmsg = ""
    while True:
        ircmsg = recv().decode()
        if ircmsg != "":
            print(bytes(ircmsg).lazy_decode())
            if ircmsg.startswith("PING "):
                ping(ircmsg)
            if len(ircmsg.split("\x01")) == 3:
                CTCPHandler(ircmsg, isRaw=True)
        if ircmsg.find("No such channel") != -1:
            log(f"Joining {chan} failed (DM)", level = "WARN")
            if origin != "null":
                sendmsg(f"{chan} is an invalid channel", origin)
            break
        elif ircmsg.find("Cannot join channel (+i)") != -1:
            log(f"Joining {chan} failed (Private)", level = "WARN")
            if origin != "null":
                sendmsg(f"Permission denied to channel {chan}", origin)
            break
        elif ircmsg.find("End of") != -1:
            log(f"Joining {chan} succeeded")
            if origin != "null":
                sendmsg(f"Joined {chan}", origin)
            chanList[chan] = 0
            break
    return chanList


def op(name, chan):
    if name != "":
        log(f"Attempting op of {name}...")
        send(f"MODE {chan} +o {name}\n")


def main():
    try:
        global ircmsg, channels, e, gmode, prefix, rebt, gblrebt, lrebt, lgblrebt, blanks
        log("Starting connection..")
        joinserver()
        if "pass" in servers[server]:
            sendmsg(f"IDENTIFY FireBot {servers[server]['pass']}", "NickServ")
            sleep(0.5)
        for chan in channels:
            joinchan(chan, "null", channels, False)
        while 1:
            global ircmsg, gmode
            raw = recv()
            ircmsg = raw.decode()
            if ircmsg == "":
                exit("Probably a netsplit")
            else:
                print(raw.lazy_decode(), sep="\n")
                if ircmsg.find("PRIVMSG") != -1:
                    # Format of ":[Nick]![ident]@[host|vhost] PRIVMSG [channel] :[message]”
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
                    log(f'Got "{bytes(message).lazy_decode()}" from "{name}" in "{chan}"')
                    if "goat" in name.lower() and gmode == True:
                        log(f"GOAT DETECTED")
                        sendmsg("Hello Goat", chan)
                        gmode = False
                    if len(name) < nicklen and chan in channels:
                        channels[chan] += 1
                    elif len(name) > nicklen:
                        log(f"Name too long ({len(name)} > {nicklen})")
                        continue
                    elif chan not in channels:
                        log(f"Channel not in channels ({chan} not in {channels})")
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
                        log(f"GOAT DETECTION ACTIVATED")
                        gmode = True
                    elif name.lower() in adminnames and mfind(
                        message, ["goat.mode.deactivate"]
                    ):
                        log(f"GOAT DETECTION DEACTIVATED")
                        gmode = False
                    elif mfind(message, ["quote"]):
                        r.seed()
                        mm = open("mastermessages.txt", "r")
                        q = mm.readlines()
                        sel = decode_escapes(
                            str(r.sample(q, 1))
                            .strip("[]'")
                            .replace("\\n", "")
                            .strip('"')
                        )
                        sendmsg(sel, chan)
                        mm.close()
                    elif mfind(message, ["join "]) and name.lower() in adminnames:
                        newchan = message.split(" ")[1].strip()
                        channels = joinchan(newchan, chan, channels)
                    elif mfind(message, ["eightball", "8ball", "8b"]):
                        if message.endswith("?"):
                            eb = open("eightball.txt", "r")
                            q = eb.readlines()
                            sel = (
                                str(r.sample(q, 1))
                                .strip("[]'")
                                .replace("\\n", "")
                                .strip('"')
                            )
                            sendmsg(f"The magic eightball says: {sel}", chan)
                            eb.close()
                        else:
                            sendmsg("Please pose a Yes or No question.", chan)
                    elif (
                        mfind(message, ["debug", "dbg"]) and name.lower() in adminnames
                    ):
                        sendmsg(f"[DEBUG] NICKLEN={nicklen}", chan)
                        sendmsg(f"[DEBUG] ADMINS={adminnames}", chan)
                        sendmsg(f"[DEBUG] CHANNELS={channels}", chan)
                    elif mfind(message, ["raw ", "cmd "]) and name.lower() in adminnames:
                        sendraw(message.split(" ", 1)[1])
                    elif (
                        mfind(message, [f"reboot {rebt}", f"reboot {gblrebt}"], False)
                        and name.lower() in adminnames
                    ):
                        for i in channels:
                            sendmsg("Rebooting...", i)
                        send("QUIT :Rebooting\n")
                        __import__("os").system(f"python3 -u ircbot.py {server}")
                        exit("Inner layer exited or crashed")
                    elif (
                        name.lower() in adminnames
                        and message.rstrip().lower() == exitcode
                    ):
                        sendmsg("oh...okay. :'(", chan)
                        for i in channels:
                            # print(f'[LOG][{server}] i="{i}" vs chan="{chan}"')
                            if i != chan.strip():
                                sendmsg("goodbye... :'(", i)
                        send("QUIT :Shutting down\n", "UTF-8")
                        log(f"QUIT")
                        exit("goodbye :'(")
                        # raise EOFError
                    elif sucheck(message):
                        if name.lower() in adminnames:
                            sendmsg(
                                "Error - system failure, contact system operator", chan
                            )
                        elif "bot" in name.lower():
                            log(f"lol, no.")
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
                        mm = open("mastermessages.txt", "r")
                        q = mm.readlines()
                        sel = decode_escapes(
                            str(r.sample(q, 1))
                            .strip("[]'")
                            .replace("\\n", "")
                            .strip('"')
                        )
                        sendmsg(f"[QUOTE] {sel}", chan)
                        mm.close()
                else:
                    if ircmsg.startswith("PING "):
                        ping(ircmsg)
                    if ircmsg.find("Closing Link") != -1:
                        exit("I got killed :'(")
                    if ircmsg.find("ERROR :Ping timeout: ") != -1:
                        exit("Ping timeout")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
