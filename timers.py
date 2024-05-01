#!/usr/bin/python3
import bare, pylast
import config as conf
import random as r
from logs import log
from typing import Any, Callable, NoReturn
from threading import Thread
from time import sleep
from traceback import format_exc


def is_dead(thr: Thread) -> bool:
    thr.join(timeout=0)
    return not thr.is_alive()


def threadWrapper(data: dict) -> NoReturn:
    if not data["noWrap"]:
        while 1:
            if data["ignoreErrors"]:
                try:
                    data["func"](*data["args"])
                except Exception:
                    Err = format_exc()
                    for line in Err.split("\n"):
                        log(line, "Thread", "WARN")
            else:
                try:
                    data["func"](*data["args"])
                except Exception:
                    Err = format_exc()
                    for line in Err.split("\n"):
                        log(line, "Thread", "CRASH")
                    exit(1)
            sleep(data["interval"])
        log("Threaded loop broken", "Thread", "FATAL")
    else:
        data["func"](*data["args"])
    exit(1)


def startThread(data: dict) -> Thread:
    t = Thread(target=threadWrapper, args=(data,))
    t.daemon = True
    t.start()
    return t


def threadManager(
    threads: dict[str, dict[str, Any]],
    output: bool = False,
    mgr: str = "TManager",
    interval: int = 60,
) -> NoReturn:
    if output:
        log("Begin init of thread manager", mgr)
    running = {}
    for name in threads:
        data = threads[name]
        running[name] = startThread(data)
    if output:
        log("All threads running, starting checkup loop", mgr)
    while 1:
        sleep(interval)
        if output:
            log("Checking threads", mgr)
        for name in running:
            t = running[name]
            if is_dead(t):
                if output:
                    log(f"Thread {name} has died, restarting", mgr, "WARN")
                data = threads[name]
                running[name] = startThread(data)
    log("Thread manager loop broken", mgr, "FATAL")
    exit(1)


def radio(instance: bare.bot) -> NoReturn:
    lastTrack = ""
    complained = False
    firstMiss = False
    while 1:
        try:
            newTrack = instance.lastfmLink.get_user("Firepup650").get_now_playing()
            if newTrack:
                complained = False
                firstMiss = False
                thisTrack = newTrack.__str__()
                if thisTrack != lastTrack:
                    lastTrack = thisTrack
                    instance.msg("f.sp " + thisTrack, "#fp-radio")
                    instance.sendraw(
                        f"TOPIC #fp-radio :Firepup radio ({thisTrack}) - https://open.spotify.com/playlist/4ctNy3O0rOwhhXIKyLvUZM"
                    )
            elif not complained:
                if not firstMiss:
                    firstMiss = True
                    continue
                instance.msg(
                    "Firepup seems to have stopped the music by mistake :/", "#fp-radio"
                )
                instance.sendraw(
                    "TOPIC #fp-radio :Firepup radio (Offline) - https://open.spotify.com/playlist/4ctNy3O0rOwhhXIKyLvUZM"
                )
                complained = True
                lastTrack = "null"
        except Exception:
            Err = format_exc()
            for line in Err.split("\n"):
                instance.log(line, "WARN")
        sleep(2)
    instance.log("Thread while loop broken", "FATAL")
    exit(1)


def mcDown(instance: bare.bot) -> None:
    instance.sendraw("TOPIC #firemc :FireMC Relay channel (offline)")


data: dict[str, dict[str, Any]] = {
    "radio": {"noWrap": True, "func": radio, "passInstance": True},
    "mc-down": {
        "noWrap": False,
        "func": mcDown,
        "passInstance": True,
        "interval": 60,
        "ignoreErrors": True,
    },
}
