#!/usr/bin/python3
from socket import socket, AF_INET, SOCK_STREAM
from overrides import bytes, bbytes
from logs import log
import re
from typing import NoReturn

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
        self.__version__ = "v1.0.5"
        self.socket = socket(AF_INET, SOCK_STREAM)
        log(f"Start init for {server}", self.server)

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

    def log(self, message: object) -> None:
        log(message, self.server)

    def exit(message: object) -> NoReturn:
        log(message, self.server, "EXIT")
        exit(1)
