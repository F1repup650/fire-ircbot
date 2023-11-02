#!/usr/bin/python3
from os import system
from time import sleep
from sys import argv as args
from threading import Thread
from datetime import datetime as dt

def launch(server: str) -> None:
    system(f"python3 -u ircbot.py {server}")


threads = {}
servers = [
    "ircnow",
    "replirc",
    "efnet",
]


def is_dead(thr):
    thr.join(timeout=0)
    return not thr.is_alive()


def start(server):
    t = Thread(target=launch, args=(server,))
    t.daemon = True
    t.start()
    return t


if __name__ == "__main__":
    print(f"[LOG][CORE][{dt.now()}] Begin initialization")
    for server in servers:
        threads[server] = start(server)
    print(f"[LOG][CORE][{dt.now()}] Started all instances. Idling...")
    while 1:
        sleep(60)
        print(f"[LOG][CORE][{dt.now()}] Running a checkup on all running instances")
        for server in threads:
            t = threads[server]
            if is_dead(t):
                print(f"[WARN][CORE][{dt.now()}] The thread for {server} died, restarting it...")
                threads[server] = start(server)
