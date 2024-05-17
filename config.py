#!/usr/bin/python3
from os import environ as env
from dotenv import load_dotenv  # type: ignore
import re, codecs
from typing import Optional, Any
import bare, pylast

load_dotenv()
__version__ = "v3.0.12"
npbase: str = (
    "\[\x0303last\.fm\x03\] [A-Za-z0-9_[\]{}\\|\-^]{1,$MAX} (is listening|last listened) to: \x02.+ - .*\x02( \([0-9]+ plays\)( \[.*\])?)?"  # pyright: ignore [reportInvalidStringEscapeSequence]
)
su = "^(su|sudo|(su .*|sudo .*))$"
servers: dict[str, dict[str, Any]] = {
    "ircnow": {
        "address": "127.0.0.1",
        "port": 6601,
        "interval": 200,
        "pass": env["ircnow_pass"],
        "channels": {"#random": 0, "#dice": 0, "#offtopic": 0, "#main/replirc": 0},
        "ignores": ["#main/replirc"],
        "hosts": ["9pfs.repl.co"],
    },
    "efnet": {
        "address": "irc.underworld.no",
        "channels": {"#random": 0, "#dice": 0},
        "hosts": ["154.sub-174-251-241.myvzw.com"],
    },
    "replirc": {
        "address": "127.0.0.1",
        "pass": env["replirc_pass"],
        "channels": {
            "#random": 0,
            "#dice": 0,
            "#main": 0,
            "#bots": 0,
            "#firebot": 0,
            "#sshchat": 0,
            "#firemc": 0,
            "#fp-radio": 0,
            "#fp-radio-debug": 0,
            "#hardfork": 0,
        },
        "ignores": ["#fp-radio"],
        "admins": ["h-tl"],
        "hosts": ["owner.firepi"],
        "threads": ["radio"],
        "autoMethod": "MARKOV",
    },
    "backupbox": {
        "address": "127.0.0.1",
        "port": 6607,
        "channels": {"#default": 0, "#botrebellion": 0, "#main/replirc": 0},
        "ignores": ["#main/replirc"],
        "hosts": [
            "172.20.171.225",
            "169.254.253.107",
            "2600-6c5a-637f-1a85-0000-0000-0000-6667.inf6.spectrum.com",
        ],
        "onIdntCmds": ["OPER e e"],
    },
    "twitch": {
        "nick": "fireschatbot",
        "address": "irc.chat.twitch.tv",
        "serverPass": env["twitch_pass"],
        "channels": {
            "#firepup650": 0,
        },
        "admins": ["firepup650"],
        "prefix": "!",
    },
}
admin_hosts: list[str] = ["firepup.firepi", "47.221.108.152"]
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
lastfmLink = pylast.LastFMNetwork(env["FM_KEY"], env["FM_SECRET"])
npallowed: list[str] = ["FireBitBot"]


def decode_escapes(s: str) -> str:
    def decode_match(match):
        return codecs.decode(match.group(0), "unicode-escape")

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


def mfind(message: str, find: list, usePrefix: bool = True) -> bool:
    if usePrefix:
        return any(message[: len(match) + 1] == prefix + match for match in find)
    else:
        return any(message[: len(match)] == match for match in find)


def sub(
    message: str, bot: bare.bot, chan: Optional[str] = "", name: Optional[str] = ""
) -> str:
    result = message.replace("$BOTNICK", bot.nick).replace("$NICK", bot.nick)
    result = result.replace("$NICKLEN", str(bot.nicklen)).replace(
        "$MAX", str(bot.nicklen)
    )
    if chan:
        result = result.replace("$CHANNEL", chan).replace("$CHAN", chan)
    if name:
        result = result.replace("$SENDER", name).replace("$NAME", name)
    return result
