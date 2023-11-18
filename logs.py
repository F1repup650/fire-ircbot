#!/usr/bin/python3
from datetime import datetime as dt
from sys import stdout, stderr
from typing import Union


def log(
    message: str,
    origin: str = "Unknown",
    level: str = "LOG",
    time: Union[dt, str] = "now",
) -> None:
    if level in ["EXIT", "CRASH"]:
        stream = stderr
    else:
        stream = stdout
    if time == "now":
        dtime = dt.now()
    elif type(time) == str:
        raise ValueError('Only "now" is an accepted string argument for time')
    elif type(time) == dt:
        dtime = time
    else:
        raise ValueError("time must either be a string or a dt object")
    time = dtime.strftime("%H:%M:%S")
    if not "\n" in message:
        print(f"[{level}][{origin}][{time}] {message}", file=stream)
    else:
        for line in message.split("\n"):
            print(f"[{level}][{origin}][{time}] {line}", file=stream)
