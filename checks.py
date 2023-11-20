#!/usr/bin/python3
import config as conf
import random as r
from typing import Any, Callable, Optional
import bare, re

def admin(bot: bare.bot, name: str, host: Optional[str] = "nul", chan: Optional[str] = "nul", cmd: Optional[str] = "nul") -> bool:
    if (
        name.lower() in conf.servers[bot.server]["admins"]
        or host in conf.admin_hosts
        or host in conf.servers[bot.server]["hosts"]
    ):
        if bot.current != "bridge":
            return True
        else:
            if type(chan) != str or chan == "nul":
                return False
            else:
                bot.msg(f"Sorry {name}, bridged users can't use admin commands.", chan)
                return False
    else:
        if type(chan) != str or chan == "nul":
            return False
        else:
            bot.msg(f"Sorry {name}, {cmd} is an admin only command.", chan)
            return False
