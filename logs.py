#!/usr/bin/python3
from datetime import datetime as dt
from sys import stdout, stderr


def log(
    message: str, origin: str = "Unknown", level: str = "LOG", time: dt = "now"
) -> None:
    if level == "EXIT":
        stream = stderr
    else:
        stream = stdout
    if time == "now":
        time = dt.now()
    if not "\n" in message:
        print(f"[{level}][{origin}][{time}] {message}")
    else:
        for line in message.split("\n"):
            print(f"[{level}][{origin}][{time}] {line}")
