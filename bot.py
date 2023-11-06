#!/usr/bin/python3
from socket import socket, AF_INET, SOCK_STREAM
from overrides import bytes, bbytes
from logs import log
import re
from typing import NoReturn
from config import npbase, servers, __version__


class bot:
    def __init__(server: str):
        self.gmode = False
        self.server = server
        self.nicklen = 30
        self.address = servers[server]["address"]
        self.port = servers[server]["port"] if "port" in servers[server] else 6667
        self.channels = servers[server]["channels"]
        self.interval = (
            servers[server]["interval"] if "interval" in servers[server] else 50
        )
        self.nick = "FireBot"
        self.prefix = "."
        self.rebt = "fire"
        self.gblrebt = "all"
        self.adminnames = servers[server]["admins"]
        self.exitcode = f"bye {self.nick.lower()}"
        self.np = re.compile(npbase.replace("MAX", f"{nicklen}"))
        self.queue = []
        self.sock = socket(AF_INET, SOCK_STREAM)
        log(f"Start init for {server}", self.server)

    def connect(self) -> None:
        self.log(f"Joining {server}...")
        self.sock.connect((self.address, self.port))
        self.send(f"USER {self.nick} {self.nick} {self.nick} {self.nick}\n")
        self.send(f"NICK {self.nick}\n")
        ircmsg = ""
        while (
            ircmsg.find(f"MODE {self.nick}") == -1
            and ircmsg.find(f"PRIVMSG {self.nick}") == -1
        ):
            ircmsg = self.recv().decode()
            if ircmsg != "":
                print(bytes(ircmsg).lazy_decode())
                if ircmsg.find("NICKLEN=") != -1:
                    self.nicklen = int(ircmsg.split("NICKLEN=")[1].split(" ")[0])
                    self.np = re.compile(npbase.replace("MAX", f"{self.nicklen}"))
                    self.log(f"NICKLEN set to {nicklen}")
                elif ircmsg.find("Nickname") != -1:
                    self.log("Nickname in use", "WARN")
                    self.nick = f"{self.nick}{r.randint(0,1000)}"
                    self.send(f"NICK {self.nick}\n")
                    self.log(f"nick is now {self.nick}")
                elif ircmsg.startswith("PING "):
                    self.ping(ircmsg)
                elif len(ircmsg.split("\x01")) == 3:
                    self.CTCPHandler(ircmsg, isRaw=True)
                elif ircmsg.find("Closing Link") != -1:
                    self.exit("Closing Link")
            else:
                self.exit("Lost connection to the server")
        self.log(f"Joined {server} successfully!")

    def join(self, chan: str) -> None:
        log(f"Joining {chan}...", server)
        chan = chan.replace(" ", "")
        if "," in chan:
            chans = chan.split(",")
            for subchan in chans:
                joinchan(subchan, origin, chanList)
            return
        if chan.startswith("0") or (chan == "#main" and lock):
            if origin != "null":
                sendmsg(f"Refusing to join channel {chan} (protected)", origin)
            return
        if chan in channels and lock:
            if origin != "null":
                sendmsg(f"I'm already in {chan}.", origin)
            return
        send(f"JOIN {chan}\n")
        while True:
            ircmsg = self.recv().decode()
            if ircmsg != "":
                code = 0
                try:
                    code = int(ircmsg.split(" ", 2)[1].strip())
                except (IndexError, ValueError):
                    pass
                print(bytes(ircmsg).lazy_decode())
                if ircmsg.startswith("PING "):
                    self.ping(ircmsg)
                elif len(ircmsg.split("\x01")) == 3:
                    CTCPHandler(ircmsg, isRaw=True)
                elif code == 403:
                    self.log(f"Joining {chan} failed", "WARN")
                    if origin != "null":
                        sendmsg(f"{chan} is an invalid channel", origin)
                    break
                elif code == 473:
                    self.log(f"Joining {chan} failed (+i)", "WARN")
                    if origin != "null":
                        sendmsg(f"{chan} is +i, and I'm not invited.", origin)
                    break
                elif code == 366:
                    log(f"Joining {chan} succeeded", server)
                    if origin != "null":
                        sendmsg(f"Joined {chan}", origin)
                    self.channels[chan] = 0
                    break

    def send(self, command: str) -> int:
        return ircsock.send(bytes(command))

    def recv(self) -> bytes:
        if self.queue:
            return bytes(self.queue.pop(0))
        data = bytes(self.sock.recv(2048).strip(b"\r\n"))
        if b"\r\n" in data:
            self.queue.extend(data.split(b"\r\n"))
            return bytes(self.queue.pop(0))
        return data

    def log(self, message: object, level: str = "LOG") -> None:
        log(message, self.server)

    def exit(message: object) -> NoReturn:
        log(message, self.server, "EXIT")
        exit(1)

    def CTCP(self, msg: str, sender: str = "", isRaw: bool = False) -> bool:
        if isRaw:
            sender = msg.split("!", 1)[0][1:]
            message = msg.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
        CTCP = msg.split("\x01")[1].split(" ", 1)[0]
        self.log(f"Responding to CTCP {CTCP} from {sender}")
        if CTCP == "VERSION":
            self.notice(
                f"\x01VERSION FireBot {__version__} (https://git.amcforum.wiki/Firepup650/fire-ircbot)\x01",
                sender,
                True,
            )
            return True
        elif CTCP == "USERINFO":
            self.notice("\x01USERINFO FireBot (Firepup's bot)\x01", sender, True)
            return True
        elif CTCP == "SOURCE":
            self.notice(
                "\x01SOURCE https://git.amcforum.wiki/Firepup650/fire-ircbot\x01",
                sender,
                True,
            )
            return True
        elif CTCP == "FINGER":
            self.notice("\x01FINGER Firepup's bot\x01", sender, True)
            return True
        elif CTCP == "CLIENTINFO":
            self.notice(
                "\x01CLIENTINFO ACTION VERSION USERINFO SOURCE FINGER\x01", sender, True
            )
            return True
        self.log(f"Unknown CTCP {CTCP}")
        return False
