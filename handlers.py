#!/usr/bin/python3
import random as r
import config as conf
import commands as cmds
from typing import Union, Callable
from overrides import bytes, bbytes
from importlib import reload
import bare, re, checks


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


def PRIVMSG(bot: bare.bot, msg: str) -> Union[tuple[None, None], tuple[str, str]]:
    # Format of ":[Nick]![ident]@[host|vhost] PRIVMSG [channel] :[message]”
    name = msg.split("!", 1)[0][1:]
    host = msg.split("@", 1)[1].split(" ", 1)[0]
    bot.tmpHost = host
    bridge = False
    bot.current = "user"
    if (
        (name.startswith("saxjax") and bot.server == "efnet")
        or (name in ["ReplIRC", "sshchat"] and bot.server == "replirc")
        or (
            name in ["FirePyLink_", "FirePyLink"]
            and bot.server in ["ircnow", "backupbox"]
        )
    ):
        if "<" in msg and ">" in msg:
            bridge = True
            bot.current = "bridge"
            Nname = msg.split("<", 1)[1].split(">", 1)[0].strip()
            if name == "ReplIRC":
                name = Nname[4:]
            elif name in ["FirePyLink_", "FirePyLink"]:
                name = Nname.lstrip("@%~+")[3:-1]
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
    message = conf.sub(message, bot, chan, name)
    if chan in bot.ignores:
        return None, None
    bot.log(
        f'Got "{bytes(message).lazy_decode()}" from "{name}" in "{chan}" ({bot.current})',
    )
    if len(name) > bot.nicklen:
        bot.log(f"Name too long ({len(name)} > {bot.nicklen})")
        if not bridge:
            return None, None
        else:
            bot.log("This user is a bridge, overriding")
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
        triggers = list(conf.sub(call, bot, chan, name).lower() for call in triggers)
        if conf.mfind(
            conf.sub(message, bot, chan, name).lower(),
            triggers,
            cmds.data[cmd]["prefix"],
        ):
            if "check" in cmds.data[cmd] and cmds.data[cmd]["check"]:
                if cmds.data[cmd]["check"](bot, name, host, chan, cmd):
                    cmds.call[cmd](bot, chan, name, message)
            else:
                cmds.call[cmd](bot, chan, name, message)
            handled = True
            break
    if not handled:
        for check in cmds.regexes:
            if re.search(
                conf.sub(check, bot, chan, name),
                message,
            ):
                cmds.call[check](bot, chan, name, message)
                handled = True
                break
    if not handled and conf.mfind(message, ["reload", "r"]):
        if checks.admin(bot, name, host, chan, "reload"):
            return "reload", chan
        handled = True
    if not handled and len(message.split("\x01")) == 3:
        if not CTCP(bot, message):
            kind = message.split("\x01")[1]
            if kind.startswith("ACTION ducks") and len(kind.split(" ", 2)) == 3:
                bot.msg(
                    f"\x01ACTION gets hit by {kind.split(' ', 2)[2]}\x01",
                    chan,
                )
            elif kind == "ACTION ducks":
                bot.msg("\x01ACTION gets hit by a duck\x01", chan)
    if chan in bot.channels and bot.channels[chan] >= bot.interval:
        sel = ""
        bot.channels[chan] = 0
        if bot.autoMethod == "QUOTE":
            r.seed()
            with open("mastermessages.txt", "r") as mm:
                sel = conf.decode_escapes(
                    r.sample(mm.readlines(), 1)[0].replace("\\n", "").replace("\n", "")
                )
        else:
            sel = bot.markov.generate_from_sentence(message)
        bot.msg(f"[{bot.autoMethod}] {sel}", chan)
    return None, None


def NICK(bot: bare.bot, msg: str) -> tuple[None, None]:
    name = msg.split("!", 1)[0][1:]
    if name == bot.nick:
        bot.nick = msg.split("NICK", 1)[1].split(":", 1)[1].strip()
    return None, None


def KICK(bot: bare.bot, msg: str) -> tuple[None, None]:
    important = msg.split("KICK", 1)[1].split(":", 1)[0].strip().split(" ")
    channel = important[0]
    kicked = important[1]
    if kicked == bot.nick:
        bot.channels.pop(channel, None)
    return None, None


def PART(bot: bare.bot, msg: str) -> tuple[None, None]:
    parted = msg.split("!", 1)[0][1:]
    channel = msg.split("PART", 1)[1].split(":", 1)[0].strip()
    if parted == bot.nick:
        bot.channels.pop(channel, None)
    return None, None


def QUIT(bot: bare.bot, msg: str) -> tuple[None, None]:
    if bot.server == "replirc":
        quitter = msg.split("!", 1)[0][1:]
        if quitter == "FireMCbot":
            bot.send("TOPIC #firemc :FireMC Relay channel (offline)\n")
    return None, None


def JOIN(bot: bare.bot, msg: str) -> tuple[None, None]:
    nick = msg.split("!", 1)[0][1:]
    hostname = msg.split("@", 1)[1].split(" ", 1)[0].strip()
    chan = msg.split("#")[-1].strip()
    if bot.dnsblMode != "none":
        dnsblStatus = conf.dnsbl(hostname)
        if dnsblStatus:
            match bot.dnsblMode:
                case "kickban":
                    bot.sendraw(f"KICK #{chan} {nick} :Sorry, but you're on the {dnsblStatus} blacklist(s).")
                    bot.sendraw(f"MODE #{chan} +b *!*@{hostname}")
                case "akill":
                    bot.sendraw(f"OS AKILL ADD *@{hostname} !P Sorry, but you're on the {dnsblStatus} blacklists(s).")
                case "kline":
                    bot.sendraw(f"KILL {nick} :Sorry, but you're on the {dnsblStatus} blacklist(s).")
                    bot.sendraw(f"KLINE 524160 *@{hostname} :Sorry, but you're on the {dnsblStatus} blacklist(s).")
                    bot.sendraw(f"KLINE *@{hostname} :Sorry, but you're on the {dnsblStatus} blacklist(s).")
                case "gline":
                    bot.sendraw(f"KILL {nick} :Sorry, but you're on the {dnsblStatus} blacklist(s).")
                    bot.sendraw(f"GLINE *@{hostname} 524160 :Sorry, but you're on the {dnsblStatus} blacklist(s).")
                    bot.sendraw(f"GLINE *@{hostname} :Sorry, but you're on the {dnsblStatus} blacklist(s).")
                case _:
                    bot.log(f'Unknown dnsbl Mode "{bot.dnsblMode}"!', "WARN")
    return None, None

def NULL(bot: bare.bot, msg: str) -> tuple[None, None]:
    return None, None


handles: dict[
    str, Callable[[bare.bot, str], Union[tuple[None, None], tuple[str, str]]]
] = {
    "PRIVMSG": PRIVMSG,
    "NICK": NICK,
    "KICK": KICK,
    "PART": PART,
    "MODE": NULL,
    "TOPIC": NULL,
    "QUIT": QUIT,
    "JOIN": JOIN,
}
