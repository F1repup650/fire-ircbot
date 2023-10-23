#!/usr/bin/python3
from os import system
from time import sleep
from sys import argv as args
from threading import Thread

call = "python3 -u ircbot.py"


def launch(server: str) -> None:
    system(f"{call} {server}")


threads = {}
servers = [
    "ircnow",
    "replirc",
    #"efnet",
]


def is_dead(thr):
    thr.join(timeout=0)
    return not thr.is_alive()


if __name__ == "__main__":
    print("[LOG][CORE] Begin initialization")
    for server in servers:
        t = Thread(target=launch, args=(server,))
        t.daemon = True
        threads[server] = t
        t.start()
    print("[LOG][CORE] Started all instances. Idling...")
    while 1:
        sleep(10)
        for server in threads:
            t = threads[server]
            if is_dead(t):
                exit(f"[EXIT][CORE] The thread for {server} died")
