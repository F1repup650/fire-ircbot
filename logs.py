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
        time = dt.now()
    if not "\n" in message:
        print(f"[{level}][{origin}][{time}] {message}", file=stream)
    else:
        for line in message.split("\n"):
            print(f"[{level}][{origin}][{time}] {line}", file=stream)
