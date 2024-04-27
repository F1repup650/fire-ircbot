#!/usr/bin/python3
from os import system
from time import sleep
from threading import Thread
from logs import log
from timers import threadManager


def launch(server: str) -> None:
    system(f"python3 -u ircbot.py {server}")


servers = {
    "ircnow": {"noWrap": True, "func": launch, "args": ["ircnow"]},
    "replirc": {"noWrap": True, "func": launch, "args": ["replirc"]},
    "efnet": {"noWrap": True, "func": launch, "args": ["efnet"]},
    "backupbox": {"noWrap": True, "func": launch, "args": ["backupbox"]},
    "twitch": {"noWrap": True, "func": launch, "args": ["twitch"]},
}


if __name__ == "__main__":
    threadManager(servers, True, "CORE")
