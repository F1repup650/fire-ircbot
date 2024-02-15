#!/usr/bin/python3
from socket import socket
from overrides import bytes, bbytes
from typing import NoReturn, Union

logs = ...
re = ...
cmds = ...
conf = ...
sleep = ...
reload = ...
r = ...
handlers = ...


def mfind(message: str, find: list, usePrefix: bool = True) -> bool:
    ...


class bot:
    gmode: bool
    server: str
    nicklen: int
    address: str
    port: int
    channels: dict[str, int]
    interval: int
    __version__: str
    nick: str
    adminnames: list[str]
    queue: list[bbytes]  # pyright: ignore [reportInvalidTypeForm]
    sock: socket
    npallowed: list[str]
    current: str
    tmpHost: str

    def __init__(self, server: str):
        ...

    def connect(self) -> None:
        ...

    def join(self, chan: str, origin: str, lock: bool = True) -> None:
        ...

    def ping(self, ircmsg: str) -> int:
        ...

    def send(self, command: str) -> int:
        ...

    def recv(self) -> bytes:
        ...

    def log(self, message: str, level: str = "LOG") -> None:
        ...

    def exit(self, message: str) -> NoReturn:
        ...

    def msg(self, msg: str, target: str) -> None:
        ...

    def op(self, name: str, chan: str) -> Union[int, None]:
        ...

    def notice(self, msg: str, target: str, silent: bool = False) -> int:
        ...

    def sendraw(self, command: str) -> int:
        ...

    def mainloop(self) -> NoReturn:
        ...
