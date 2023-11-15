from subprocess import run, PIPE
import config as conf
import random as r
from typing import Any, Callable
import bare


def goat(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.log("GOAT DETECTED")
    bot.msg("Hello Goat", chan)
    bot.gmode = False


def botlist(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.msg(
        f"Hi! I'm FireBot (https://git.amcforum.wiki/Firepup650/fire-ircbot)! My admins on this server are {bot.adminnames}.",
        chan,
    )


def bugs(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.msg(
        f"\x01ACTION realizes {name} looks like a bug, and squashes {name}\x01",
        chan,
    )


def hi(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.msg(f"Hello {name}!", chan)


def op(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.op(name, chan)


def ping(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.msg(
        f"{name}: pong",
        chan,
    )


def uptime(bot: bare.bot, chan: str, name: str, message: str) -> None:
    uptime = run(["uptime", "-p"], stdout=PIPE).stdout.decode().strip()
    bot.msg(
        f"Uptime: {uptime}",
        chan,
    )


def isAdmin(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.msg(
        f"{conf.adminCheck(bot, name)} (hostname is not checked)",
        chan,
    )


def help(bot: bare.bot, chan: str, name: str, message: str) -> None:
    helpErr = False
    if (name.startswith("saxjax") and bot.server == "efnet") or (
        name == "ReplIRC" and bot.server == "replirc"
    ):
        if "<" in message and "<" in message:
            helpErr = True
    elif name.endswith("dsc"):
        helpErr = True
    if not helpErr:
        bot.msg("Command list needs rework", name)
        return
        bot.msg("List of commands:", name)
        bot.msg(f'Current bot.prefix is "{bot.prefix}"', name)
        bot.msg(f"{bot.prefix}help - Sends this help list", name)
        bot.msg(f"{bot.prefix}quote - Sends a random firepup quote", name)
        bot.msg(
            f"{bot.prefix}(eightball,8ball,8b) [question]? - Asks the magic eightball a question",
            name,
        )
        bot.msg(f"(hi,hello) {bot.nick} - The bot says hi to you", name)
        if name.lower() in bot.adminnames:
            bot.msg(f"reboot {bot.rebt} - Restarts the bot", name)
            bot.msg("op me - Makes the bot try to op you", name)
            bot.msg(
                f"{bot.prefix}join [channel(s)] - Joins the bot to the specified channel(s)",
                name,
            )
    else:
        bot.msg("Sorry, I can't send help to bridged users.", chan)


def goatOn(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.log("GOAT DETECTION ACTIVATED")
    bot.gmode = True


def goatOff(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.log("GOAT DETECTION DEACTIVATED")
    bot.gmode = False


def quote(bot: bare.bot, chan: str, name: str, message: str) -> None:
    r.seed()
    mm = open("mastermessages.txt", "r")
    q = mm.readlines()
    sel = conf.decode_escapes(str(r.sample(q, 1)).strip("[]'").replace("\\n", "").strip('"'))
    bot.msg(sel, chan)
    mm.close()


def join(bot: bare.bot, chan: str, name: str, message: str) -> None:
    newchan = message.split(" ", 1)[1].strip()
    bot.join(newchan, chan)


def eball(bot: bare.bot, chan: str, name: str, message: str) -> None:
    if message.endswith("?"):
        eb = open("eightball.txt", "r")
        q = eb.readlines()
        sel = str(r.sample(q, 1)).strip("[]'").replace("\\n", "").strip('"')
        bot.msg(f"The magic eightball says: {sel}", chan)
        eb.close()
    else:
        bot.msg("Please pose a Yes or No question.", chan)


def debug(bot: bare.bot, chan: str, name: str, message: str) -> None:
    dbg_out = {
        "VERSION": bot.__version__,
        "NICKLEN": bot.nicklen,
        "NICK": bot.nick,
        "ADMINS": conf.servers[bot.server]["hosts"] + " (Does not include hostname checks)",
        "CHANNELS": bot.channels,
    }
    bot.msg(f"[DEBUG] {dbg_out}", chan)


def raw(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.sendraw(message.split(" ", 1)[1])


def reboot(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.send("QUIT :Rebooting\n")
    bot.exit("Reboot")


def sudo(bot: bare.bot, chan: str, name: str, message: str) -> None:
    if conf.adminCheck(bot, name):
        bot.msg("Error - system failure, contact system operator", chan)
    elif "bot" in name.lower():
        bot.log("lol, no.")
    else:
        bot.msg("Access Denied", chan)


def nowplaying(bot: bare.bot, chan: str, name: str, message: str) -> None:
    if name in bot.npallowed:
        x02 = "\x02"
        bot.msg(
            f"f.sp {message.split(x02)[1]}",
            chan,
        )


data: dict[str, dict[str, Any]] = {
    "!botlist": {"prefix": False, "aliases": []},
    "bugs bugs bugs": {"prefix": False, "aliases": []},
    "hi $BOTNICK": {"prefix": False, "aliases": ["hello $BOTNICK"]},
    #   [npbase, su]
    "restart": {"prefix": True, "aliases": ["reboot"], "admin": True},
    "uptime": {"prefix": True, "aliases": []},
    "raw ": {"prefix": True, "aliases": ["cmd "], "admin": True},
    "debug": {"prefix": True, "aliases": ["dbg"], "admin": True},
    "8ball": {"prefix": True, "aliases": ["eightball", "8b"]},
    "join ": {"prefix": True, "aliases": [], "admin": True},
    "quote": {"prefix": True, "aliases": ["q"]},
    "goat.mode.activate": {"prefix": True, "aliases": [], "admin": True},
    "goat.mode.deactivate": {"prefix": True, "aliases": [], "admin": True},
    "help": {"prefix": True, "aliases": []},
    "amiadmin": {"prefix": True, "aliases": []},
    "ping": {"prefix": True, "aliases": []},
    "op me": {"prefix": False, "aliases": [], "admin": True},
}
checks: list[str] = [conf.npbase, conf.su]
call: dict[str, Callable[[bare.bot, str, str, str], None]] = {
    "!botlist": botlist,
    "bugs bugs bugs": bugs,
    "hi $BOTNICK": hi,
    conf.npbase: nowplaying,
    conf.su: sudo,
    "restart": reboot,
    "uptime": uptime,
    "raw ": raw,
    "debug": debug,
    "8ball": eball,
    "join ": join,
    "quote": quote,
    "goat.mode.activate": goatOn,
    "goat.mode.decativate": goatOff,
    "help": help,
    "amiadmin": isAdmin,
    "ping": ping,
    "op me": op,
}
