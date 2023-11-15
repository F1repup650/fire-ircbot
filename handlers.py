import random as r
import config as conf
import re
import commands as cmds
from typing import Union
from overrides import bytes, bbytes
from importlib import reload
import bare


def CTCP(bot: bare.bot, msg: str) -> bool:
    sender = msg.split("!", 1)[0][1:]
    kind = msg.split("\x01")[1].split(" ", 1)[0]
    bot.log(f'Responding to CTCP "{kind}" from {sender}')
    if kind == "VERSION":
        bot.notice(
            f"\x01VERSION FireBot {conf.__version__} (https://git.amcforum.wiki/Firepup650/fire-ircbot)\x01",
            sender,
            True,
        )
        return True
    elif kind == "USERINFO":
        bot.notice("\x01USERINFO FireBot (Firepup's bot)\x01", sender, True)
        return True
    elif kind == "SOURCE":
        bot.notice(
            "\x01SOURCE https://git.amcforum.wiki/Firepup650/fire-ircbot\x01",
            sender,
            True,
        )
        return True
    elif kind == "FINGER":
        bot.notice("\x01FINGER Firepup's bot\x01", sender, True)
        return True
    elif kind == "CLIENTINFO":
        bot.notice(
            "\x01CLIENTINFO ACTION VERSION USERINFO SOURCE FINGER\x01", sender, True
        )
        return True
    bot.log(f'Unknown CTCP "{kind}"', "WARN")
    return False


def PRIVMSG(bot: bare.bot, msg: str) -> tuple[Union[None, str], Union[None, str]]:
    # Format of ":[Nick]![ident]@[host|vhost] PRIVMSG [channel] :[message]”
    name = msg.split("!", 1)[0][1:]
    if (name.startswith("saxjax") and bot.server == "efnet") or (
        name == "ReplIRC" and bot.server == "replirc"
    ) or (name == "FirePyLink_" and bot.server == "ircnow"):
        if "<" in msg and ">" in msg:
            Nname = msg.split("<", 1)[1].split(">", 1)[0].strip()
            if name == "ReplIRC":
                name = Nname[4:]
            else:
                name = Nname
            message = msg.split(">", 1)[1].strip()
        else:
            message = msg.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
    elif name == bot.nick:
        return None, None
    else:
        message = msg.split("PRIVMSG", 1)[1].split(":", 1)[1].strip()
    chan = msg.split("PRIVMSG", 1)[1].split(":", 1)[0].strip()
    bot.log(
        f'Got "{bytes(message).lazy_decode()}" from "{name}" in "{chan}"',
    )
    if len(name) > bot.nicklen:
        bot.log(f"Name too long ({len(name)} > {bot.nicklen})")
        return None, None
    elif chan not in bot.channels:
        if not chan == bot.nick:
            bot.log(
                f"Channel not in channels ({chan} not in {bot.channels})",
                "WARN",
            )
        if not chan.startswith(("#", "+", "&")):
            chan = name
    else:
        bot.channels[chan] += 1
    if "goat" in name.lower() and bot.gmode == True:
        cmds.goat(bot, chan, name, message)
    handled = False
    for cmd in cmds.data:
        triggers = [cmd]
        triggers.extend(cmds.data[cmd]["aliases"])
        triggers = list(call.replace("$BOTNICK", bot.nick.lower()) for call in triggers)
        if conf.mfind(
            message.lower(),
            triggers,
            cmds.data[cmd]["prefix"],
        ):
            if (
                "admin" in cmds.data[cmd] and cmds.data[cmd]["admin"]
            ) and name not in bot.adminnames:
                bot.msg(
                    f"Sorry {name}, you don't have permission to use {cmd.strip()}.",
                    chan,
                )
            else:
                cmds.call[cmd](bot, chan, name, message)
            handled = True
            break
    if not handled:
        for check in cmds.checks:
            if re.search(
                check.replace("$MAX", str(bot.nicklen)).replace("$BOTNICK", bot.nick),
                message,
            ):
                cmds.call[check](bot, chan, name, message)
                handled = True
                break
    if not handled and conf.mfind(message, ["reload"]):
        if name in bot.adminnames:
            return "reload", chan
        else:
            bot.msg(
                f"Sorry {name}, you don't have permission to use reload.",
                chan,
            )
        handled = True
    if not handled and len(message.split("\x01")) == 3:
        if not CTCP(bot, message):
            kind = message.split("\x01")[1]
            if kind == "ACTION ducks":
                bot.msg("\x01ACTION gets hit by a duck\x01", chan)
            elif kind.startswith("ACTION ducks"):
                bot.msg(
                    f"\x01ACTION gets hit by {kind.split(' ', 2)[2]}\x01",
                    chan,
                )
    if chan in bot.channels and bot.channels[chan] >= bot.interval:
        r.seed()
        bot.channels[chan] = 0
        mm = open("mastermessages.txt", "r")
        q = mm.readlines()
        sel = conf.decode_escapes(
            str(r.sample(q, 1)).strip("[]'").replace("\\n", "").strip('"')
        )
        bot.msg(f"[QUOTE] {sel}", chan)
        mm.close()
    return None, None


handles = {"PRIVMSG": PRIVMSG}
