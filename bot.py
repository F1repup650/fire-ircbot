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

def mfind(message: str, find: list, usePrefix: bool = True) -> bool:
    if usePrefix:
        return any(message[: len(match) + 1] == conf.prefix + match for match in find)
    else:
        return any(message[: len(match)] == match for match in find)

class bot:
    def __init__(self, server: str):
        self.gmode = False
        self.server = server
        self.nicklen = 30
        self.address = conf.servers[server]["address"]
        self.port = conf.servers[server]["port"] if "port" in conf.servers[server] else 6667
        self.channels = conf.servers[server]["channels"]
        self.interval = (
            conf.servers[server]["interval"] if "interval" in conf.servers[server] else 50
        )
        self.__version__ = conf.__version__
        self.nick = "FireBot"
        self.rebt = "fire"
        self.gblrebt = "all"
        self.adminnames = conf.servers[server]["admins"]
        self.exitcode = f"bye {self.nick.lower()}"
        self.queue = []
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.log(f"Start init for {self.server}")

    def connect(self) -> None:
        self.log(f"Joining {self.server}...")
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
                    self.log(f"NICKLEN set to {self.nicklen}")
                elif ircmsg.find("Nickname") != -1:
                    self.log("Nickname in use", "WARN")
                    self.nick = f"{self.nick}{r.randint(0,1000)}"
                    self.send(f"NICK {self.nick}\n")
                    self.log(f"nick is now {self.nick}")
                elif ircmsg.startswith("PING "):
                    self.ping(ircmsg)
                elif len(ircmsg.split("\x01")) == 3:
                    self.CTCP(ircmsg, isRaw=True)
                elif ircmsg.find("Closing Link") != -1:
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
        if chan.startswith("0") or (chan == "#main" and lock):
            if origin != "null":
                self.sendmsg(f"Refusing to join channel {chan} (protected)", origin)
            return
        if chan in self.channels and lock:
            if origin != "null":
                self.sendmsg(f"I'm already in {chan}.", origin)
            return
        self.send(f"JOIN {chan}\n")
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
                    self.CTCP(ircmsg, isRaw=True)
                elif code == 403:
                    self.log(f"Joining {chan} failed", "WARN")
                    if origin != "null":
                        sendmsg(f"{chan} is an invalid channel", origin)
                    break
                elif code == 473:
                    self.log(f"Joining {chan} failed (+i)", "WARN")
                    if origin != "null":
                        self.sendmsg(f"{chan} is +i, and I'm not invited.", origin)
                    break
                elif code == 520:
                    self.log(f"Joining {chan} failed (+O)", "WARN")
                    if origin != "null":
                        self.sendmsg(f"{chan} is +O, and I'm not an operator.", origin)
                elif code == 366:
                    self.log(f"Joining {chan} succeeded")
                    if origin != "null":
                        self.sendmsg(f"Joined {chan}", origin)
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

    def log(self, message: object, level: str = "LOG") -> None:
        logs.log(message, self.server)

    def exit(self, message: object) -> NoReturn:
        logs.log(message, self.server, "EXIT")
        exit(1)

    def CTCP(self, msg: str, sender: str = "", isRaw: bool = False) -> bool:
        if isRaw:
            sender = msg.split("!", 1)[0][1:]
            message = msg.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
        kind = msg.split("\x01")[1].split(" ", 1)[0]
        self.log(f"Responding to CTCP \"{kind}\" from {sender}")
        if kind == "VERSION":
            self.notice(
                f"\x01VERSION FireBot {conf.__version__} (https://git.amcforum.wiki/Firepup650/fire-ircbot)\x01",
                sender,
                True,
            )
            return True
        elif kind == "USERINFO":
            self.notice("\x01USERINFO FireBot (Firepup's bot)\x01", sender, True)
            return True
        elif kind == "SOURCE":
            self.notice(
                "\x01SOURCE https://git.amcforum.wiki/Firepup650/fire-ircbot\x01",
                sender,
                True,
            )
            return True
        elif kind == "FINGER":
            self.notice("\x01FINGER Firepup's bot\x01", sender, True)
            return True
        elif kind == "CLIENTINFO":
            self.notice(
                "\x01CLIENTINFO ACTION VERSION USERINFO SOURCE FINGER\x01", sender, True
            )
            return True
        self.log(f"Unknown CTCP \"{kind}\"", "WARN")
        return False

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
            self.msg(f"IDENTIFY FireBot {conf.servers[self.server]['pass']}", "NickServ")
        sleep(0.5)
        for chan in self.channels:
            self.join(chan, "null", False)
        while 1:
            raw = self.recv()
            ircmsg = raw.decode()
            if ircmsg == "":
                self.exit("Probably a netsplit")
            else:
                print(raw.lazy_decode(), sep="\n")
                action = "Unknown"
                try:
                    action = ircmsg.split(" ", 2)[1].strip()
                except IndexError:
                    pass
                if action == "PRIVMSG":
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
                    self.log(
                        f'Got "{bytes(message).lazy_decode()}" from "{name}" in "{chan}"',
                    )
                    if len(name) > self.nicklen:
                        self.log(f"Name too long ({len(name)} > {self.nicklen})")
                        continue
                    elif chan not in self.channels:
                        self.log(
                            f"Channel not in channels ({chan} not in {self.channels})",
                            "WARN",
                        )
                        if not chan.startswith(("#", "+", "&")):
                            chan = name
                    else:
                        self.channels[chan] += 1
                    if "goat" in name.lower() and self.gmode == True:
                        cmds.goat(self, chan)
                    handled = False
                    for cmd in cmds.data:
                        triggers = [cmd]
                        triggers.extend(cmds.data[cmd]["aliases"])
                        triggers = list(call.replace("$BOTNICK", self.nick) for call in triggers)
                        if mfind(
                            message,
                            triggers,
                            cmds.data[cmd]["prefix"],
                        ):
                            if ("admin" in cmds.data[cmd] and cmds.data[cmd]["admin"]) and name not in self.adminnames:
                                self.msg(f"Sorry {name}, you don't have permission to use {cmd}.", chan)
                            else:
                                cmds.call[cmd](self, chan, name, message)
                            handled = True
                            break
                    if not handled:
                        for check in cmds.checks:
                            if re.search(
                                check.replace("$MAX", str(self.nicklen)).replace(
                                    "$BOTNICK", self.nick
                                ),
                                message,
                            ):
                                cmds.call[check](self, chan, name, message)
                                handled = True
                                break
                    if not handled and mfind(message, ["reload"]):
                        if name in self.adminnames:
                            reload(conf)
                            reload(cmds)
                            self.__version__ = conf.__version__
                            self.msg("Reloaded config and commands", chan)
                        else:
                            self.msg(f"Sorry {name}, you don't have permission to use reload.", chan)
                        handled = True
                    if not handled and len(message.split("\x01")) == 3:
                        if not self.CTCP(message, name):
                            CTCP = message.split("\x01")[1]
                            if CTCP == "ACTION ducks":
                                self.msg("\x01ACTION gets hit by a duck\x01", chan)
                            elif CTCP.startswith("ACTION ducks"):
                                self.msg(
                                    f"\x01ACTION gets hit by {CTCP.split(' ', 2)[2]}\x01",
                                    chan,
                                )
                    if chan in self.channels and self.channels[chan] >= self.interval:
                        r.seed()
                        self.channels[chan] = 0
                        mm = open("mastermessages.txt", "r")
                        q = mm.readlines()
                        sel = conf.decode_escapes(
                            str(r.sample(q, 1))
                            .strip("[]'")
                            .replace("\\n", "")
                            .strip('"')
                        )
                        self.msg(f"[QUOTE] {sel}", chan)
                        mm.close()
                else:
                    if ircmsg.startswith("PING "):
                        self.ping(ircmsg)
                    elif ircmsg.startswith("ERROR :Closing Link"):
                        self.exit("I got killed :'(")
                    elif ircmsg.startswith("ERROR :Ping "):
                        self.exit("Ping timeout")
