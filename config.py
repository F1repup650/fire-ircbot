#!/usr/bin/python3
from os import environ as env
from dotenv import load_dotenv
import re, codecs
from typing import Union, Any

load_dotenv()
__version__ = "v2.0.3"
npbase: str = "\[\x0303last\.fm\x03\] [A-Za-z0-9_[\]{}\\|^]{1,$MAX} (is listening|last listened) to: \x02.+ - .*\x02( \([0-9]+ plays\)( \[.*\])?)?"
su = "^(su|sudo|(su .*|sudo .*))$" # type: ignore
servers: dict[str, dict[str, Any]] = {
    "ircnow": {
        "address": "localhost",
        "port": 6601,
        "interval": 200,
        "pass": env["ircnow_pass"],
        "channels": {"#random": 0, "#dice": 0, "#offtopic": 0},
        "admins": ["firepup", "h|thelounge", "firepup|lounge"],
    },
    "efnet": {
        "address": "irc.mzima.net",
        "channels": {"#random": 0, "#dice": 0},
        "admins": ["firepup", "h|tl"],
    },
    "replirc": {
        "address": "localhost",
        "pass": env["replirc_pass"],
        "channels": {"#random": 0, "#dice": 0, "#main": 0, "#bots": 0, "#firebot": 0},
        "admins": ["firepup", "firepup|lounge", "h|tl"],
    },
}
ESCAPE_SEQUENCE_RE = re.compile(
    r"""
    ( \\U........      # 8-digit hex escapes
    | \\u....          # 4-digit hex escapes
    | \\x..            # 2-digit hex escapes
    | \\[0-7]{1,3}     # Octal escapes
    | \\N\{[^}]+\}     # Unicode characters by name
    | \\[\\'"abfnrtv]  # Single-character escapes
    )""",
    re.UNICODE | re.VERBOSE,
)
prefix = "."


def decode_escapes(s: str) -> str:
    def decode_match(match):
        return codecs.decode(match.group(0), "unicode-escape")

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


def mfind(message: str, find: list, usePrefix: bool = True) -> bool:
    if usePrefix:
        return any(message[: len(match) + 1] == prefix + match for match in find)
    else:
        return any(message[: len(match)] == match for match in find)
