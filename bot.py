#!/usr/bin/python3
from socket import socket, AF_INET, SOCK_STREAM
from overrides import bytes, bbytes
import logs
import re
from typing import NoReturn, Union
import commands as cmds
import config as conf
from time import sleep
from importlib import reload
import random as r
import handlers
import bare


def mfind(message: str, find: list, usePrefix: bool = True) -> bool:
    if usePrefix:
        return any(message[: len(match) + 1] == conf.prefix + match for match in find)
    else:
        return any(message[: len(match)] == match for match in find)


class bot(bare.bot):
    def __init__(self, server: str):
        self.gmode = False
        self.server = server
        self.nicklen = 30
        self.address = conf.servers[server]["address"]
        self.port = (
            conf.servers[server]["port"] if "port" in conf.servers[server] else 6667
        )
        self.channels = conf.servers[server]["channels"]
        self.interval = (
            conf.servers[server]["interval"]
            if "interval" in conf.servers[server]
            else 50
        )
        self.__version__ = conf.__version__
        self.nick = "FireBot"
        self.adminnames = conf.servers[server]["admins"]
        self.queue: list[bbytes] = []  # pyright: ignore [reportInvalidTypeForm]
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.npallowed = ["FireBitBot"]
        self.current = "user"
        self.log(f"Start init for {self.server}")

    def connect(self) -> None:
        self.log(f"Joining {self.server}...")
        self.sock.connect((self.address, self.port))
        self.send(f"USER {self.nick} {self.nick} {self.nick} {self.nick}\n")
        self.send(f"NICK {self.nick}\n")
        ircmsg = ""
        while True:
            ircmsg = self.recv().safe_decode()
            if ircmsg != "":
                code = 0
                try:
                    code = int(ircmsg.split(" ", 2)[1].strip())
                except (IndexError, ValueError):
                    pass
                print(bytes(ircmsg).lazy_decode())
                if "NICKLEN" in ircmsg:
                    self.nicklen = int(ircmsg.split("NICKLEN=")[1].split(" ")[0])
                    self.log(f"NICKLEN set to {self.nicklen}")
                if code == 433:
                    self.log("Nickname in use", "WARN")
                    self.nick = f"{self.nick}{r.randint(0,1000)}"
                    self.send(f"NICK {self.nick}\n")
                    self.log(f"nick is now {self.nick}")
                if code in [376, 422]:
                    self.log(f"Success by code: {code}")
                    break
                if " MODE " in ircmsg or " PRIVMSG " in ircmsg:
                    self.log(f"Success by MSG/MODE")
                    break
                if ircmsg.startswith("PING "):
                    self.ping(ircmsg)
                if len(ircmsg.split("\x01")) == 3:
                    handlers.CTCP(self, ircmsg)
                if "Closing link" in ircmsg:
                    self.exit("Closing Link")
            else:
                self.exit("Lost connection to the server")
        self.log(f"Joined {self.server} successfully!")

    def join(self, chan: str, origin: str, lock: bool = True) -> None:
        self.log(f"Joining {chan}...")
        chan = chan.replace(" ", "")
        if "," in chan:
            chans = chan.split(",")
            for subchan in chans:
                self.join(subchan, origin)
            return
        if chan.startswith("0") or (
            chan == "#main" and lock and self.server != "replirc"
        ):
            if origin != "null":
                self.msg(f"Refusing to join channel {chan} (protected)", origin)
            return
        if chan in self.channels and lock:
            if origin != "null":
                self.msg(f"I'm already in {chan}.", origin)
            return
        self.send(f"JOIN {chan}\n")
        while True:
            ircmsg = self.recv().safe_decode()
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
                    handlers.CTCP(self, ircmsg)
                elif code == 403:
                    self.log(f"Joining {chan} failed", "WARN")
                    if origin != "null":
                        self.msg(f"{chan} is an invalid channel", origin)
                    break
                elif code == 473:
                    self.log(f"Joining {chan} failed (+i)", "WARN")
                    if origin != "null":
                        self.msg(f"{chan} is +i, and I'm not invited.", origin)
                    break
                elif code == 474:
                    self.log(f"Joining {chan} failed (+b)", "WARN")
                    if origin != "null":
                        self.msg(f"I'm banned from {chan}.", origin)
                    break
                elif code == 520:
                    self.log(f"Joining {chan} failed (+O)", "WARN")
                    if origin != "null":
                        self.msg(f"{chan} is +O, and I'm not an operator.", origin)
                    break
                elif code == 405:
                    self.log(f"Joining {chan} failed (too many channels)", "WARN")
                    if origin != "null":
                        self.msg(f"I'm in too many channels to join {chan}", origin)
                    break
                elif code == 471:
                    self.log(f"Joining {chan} failed (+l)", "WARN")
                    if origin != "null":
                        self.msg(f"{chan} is +l, and is full", origin)
                    break
                elif code == 366:
                    self.log(f"Joining {chan} succeeded")
                    if origin != "null":
                        self.msg(f"Joined {chan}", origin)
                    self.channels[chan] = 0
                    break

    def ping(self, ircmsg: str) -> int:
        pong = f"PONG :{ircmsg.split('PING :')[1]}\n"
        print(pong, end="")
        return self.send(pong)

    def send(self, command: str) -> int:
        return self.sock.send(bytes(command))

    def recv(self) -> bytes:
        if self.queue:
            return bytes(self.queue.pop(0))
        data = bytes(self.sock.recv(2048).strip(b"\r\n"))
        if b"\r\n" in data:
            self.queue.extend(data.split(b"\r\n"))
            return bytes(self.queue.pop(0))
        return data

    def log(self, message: str, level: str = "LOG") -> None:
        logs.log(message, self.server, level)

    def exit(self, message: str) -> NoReturn:
        logs.log(message, self.server, "EXIT")
        exit(1)

    def msg(self, msg: str, target: str) -> None:
        if not (target == "NickServ" and mfind(msg, ["IDENTIFY"], False)):
            self.log(f"Sending {bytes(msg).lazy_decode()} to {target}")
        else:
            self.log("Identifying myself...")
        self.send(f"PRIVMSG {target} :{msg}\n")

    def op(self, name: str, chan: str) -> Union[int, None]:
        if name != "":
            self.log(f"Attempting op of {name} in {chan}...")
            return self.send(f"MODE {chan} +o {name}\n")
        return None

    def notice(self, msg: str, target: str, silent: bool = False) -> int:
        if not silent:
            self.log(f"Sending {bytes(msg).lazy_decode()} to {target} (NOTICE)")
        return self.send(f"NOTICE {target} :{msg}\n")

    def sendraw(self, command: str) -> int:
        self.log(f"RAW sending {command}")
        command = f"{command}\n"
        return self.send(command.replace("$BOTNICK", self.nick))

    def mainloop(self) -> NoReturn:
        self.log("Starting connection..")
        self.connect()
        if "pass" in conf.servers[self.server]:
            self.msg(
                f"IDENTIFY FireBot {conf.servers[self.server]['pass']}", "NickServ"
            )
        sleep(0.5)
        for chan in self.channels:
            self.join(chan, "null", False)
        while 1:
            raw = self.recv()
            ircmsg = raw.safe_decode()
            if ircmsg == "":
                self.exit("Probably a netsplit")
            else:
                print(raw.lazy_decode(), sep="\n")
                action = "Unknown"
                try:
                    action = ircmsg.split(" ", 2)[1].strip()
                except IndexError:
                    pass
                self.tmpHost = ""
                if action in handlers.handles:
                    res, chan = handlers.handles[action](self, ircmsg)
                    if res == "reload" and type(chan) == str:
                        reload(conf)
                        self.__version__ = conf.__version__
                        reload(cmds)
                        reload(handlers)
                        self.msg("Reloaded successfully", chan)
                else:
                    if ircmsg.startswith("PING "):
                        self.ping(ircmsg)
                    elif ircmsg.startswith("ERROR :Closing Link"):
                        self.exit("I got killed :'(")
                    elif ircmsg.startswith("ERROR :Ping "):
                        self.exit("Ping timeout")
        self.exit("While loop broken")
