#!/usr/bin/python3
from os import environ as env
from dotenv import load_dotenv
load_dotenv()
__version__ = "v1.0.5"
npbase = "\[\x0303last\.fm\x03\] [A-Za-z0-9_[\]{}\\|^]{1,MAX} (is listening|last listened) to: \x02.+ - .*\x02( \([0-9]+ plays\)( \[.*\])?)?"
su = "^(su|sudo|(su .*|sudo .*))$"
servers = {
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
