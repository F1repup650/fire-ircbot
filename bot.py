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
        self.prefix = "."
        self.rebt = "fire"
        self.gblrebt = "all"
        self.lrebt = 7 + len(rebt)
        self.lgblrebt = 7 + len(gblrebt)
        self.adminnames = servers[server]["admins"]
        self.exitcode = f"bye {botnick.lower()}"
        self.np = re.compile(npbase.replace("MAX", f"{nicklen}"))
        self.queue = []
        self.socket = socket(AF_INET, SOCK_STREAM)
        log(f"Start init for {server}", self.server)

    def connect(self) -> None:
        self.log(f"Joining {server}...")
        self.socket.connect((self.address, self.port))
        self.send(f"USER {botnick} {botnick} {botnick} {botnick}\n")
        self.send(f"NICK {botnick}\n")
        while (
            ircmsg.find("MODE " + botnick) == -1
            and ircmsg.find("PRIVMSG " + botnick) == -1
        ):
            ircmsg = self.recv().decode()
            if ircmsg != "":
                print(bytes(ircmsg).lazy_decode())
                if ircmsg.find("NICKLEN=") != -1:
                    self.nicklen = int(ircmsg.split("NICKLEN=")[1].split(" ")[0])
                    self.np = re.compile(npbase.replace("MAX", f"{nicklen}"))
                    self.log(f"NICKLEN set to {nicklen}")
                elif ircmsg.find("Nickname") != -1:
                    self.log("Nickname in use", "WARN")
                    self.botnick = f"{botnick}{r.randint(0,1000)}"
                    self.send(f"NICK {botnick}\n")
                    self.log(f"botnick is now {botnick}")
                elif ircmsg.startswith("PING "):
                    self.ping(ircmsg)
                elif len(ircmsg.split("\x01")) == 3:
                    self.CTCPHandler(ircmsg, isRaw=True)
                elif ircmsg.find("Closing Link") != -1:
                    self.exit("Closing Link")
            else:
                self.exit("Lost connection to the server")
        self.log(f"Joined {server} successfully!")

    def send(self, command: str) -> int:
        return ircsock.send(bytes(command))

    def recv(self) -> bytes:
        if self.queue:
            return bytes(self.queue.pop(0))
        data = bytes(self.socket.recv(2048).strip(b"\r\n"))
        if b"\r\n" in data:
            self.queue.extend(data.split(b"\r\n"))
            return bytes(self.queue.pop(0))
        return data

    def log(self, message: object, level: str = "LOG") -> None:
        log(message, self.server)

    def exit(message: object) -> NoReturn:
        log(message, self.server, "EXIT")
        exit(1)
