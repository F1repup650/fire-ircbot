#!/usr/bin/python3
from os import system
from time import sleep
from threading import Thread
from logs import log


def launch(server: str) -> None:
    system(f"python3 -u ircbot.py {server}")


threads = {}
servers = [
    "ircnow",
    "replirc",
    "efnet",
]


def is_dead(thr: Thread) -> bool:
    thr.join(timeout=0)
    return not thr.is_alive()


def start(server: str) -> Thread:
    t = Thread(target=launch, args=(server,))
    t.daemon = True
    t.start()
    return t


if __name__ == "__main__":
    log("Begin initialization", "CORE")
    for server in servers:
        threads[server] = start(server)
    log("Started all instances. Idling...", "CORE")
    while 1:
        sleep(60)
        log("Running a checkup on all running instances", "CORE")
        for server in threads:
            t = threads[server]
            if is_dead(t):
                log(f"The thread for {server} died, restarting it...", "CORE", "WARN")
                threads[server] = start(server)
