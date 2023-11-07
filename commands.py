from subprocess import run, PIPE
from config import npbase, su, decode_escapes
import random as r

def goat(bot, chan: str, name: str, message: str) -> None:
    bot.log("GOAT DETECTED")
    bot.msg("Hello Goat", chan)


def botlist(bot, chan: str, name: str, message: str) -> None:
    bot.msg(
        f"Hi! I'm FireBot (https://git.amcforum.wiki/Firepup650/fire-ircbot)! My admins on this server are {bot.adminnames}.",
        chan,
    )


def bugs(bot, chan: str, name: str, message: str) -> None:
    bot.msg(
        f"\x01ACTION realizes {name} looks like a bug, and squashes {name}\x01",
        chan,
    )


def hi(bot, chan: str, name: str, message: str) -> None:
    bot.msg(f"Hello {name}!", chan)


def op(bot, chan: str, name: str, message: str) -> None:
    bot.op(name, chan)


def ping(bot, chan: str, name: str, message: str) -> None:
    bot.msg(
        f"{name}: pong",
        chan,
    )


def uptime(bot, chan: str, name: str, message: str) -> None:
    uptime = run(["uptime", "-p"], stdout=PIPE).stdout.decode().strip()
    bot.msg(
        f"Uptime: {uptime}",
        chan,
    )


def isAdmin(bot, chan: str, name: str, message: str) -> None:
    bot.msg(
        f"{name.lower()} in {bot.adminnames} == {name.lower() in bot.adminnames}",
        chan,
    )


def help(bot, chan: str, name: str, message: str) -> None:
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
        bot.msg(f"(hi,hello) {botnick} - The bot says hi to you", name)
        if name.lower() in bot.adminnames:
            bot.msg(f"reboot {bot.rebt} - Restarts the bot", name)
            bot.msg("op me - Makes the bot try to op you", name)
            bot.msg(
                f"{bot.prefix}join [channel(s)] - Joins the bot to the specified channel(s)",
                name,
            )
    else:
        bot.msg("Sorry, I can't send help to bridged users.", chan)


def goatOn(bot, chan: str, name: str, message: str) -> None:
    bot.log("GOAT DETECTION ACTIVATED")
    bot.gmode = True


def goatOff(bot, chan: str, name: str, message: str) -> None:
    bot.log("GOAT DETECTION DEACTIVATED")
    bot.gmode = False


def quote(bot, chan: str, name: str, message: str) -> None:
    r.seed()
    mm = open("mastermessages.txt", "r")
    q = mm.readlines()
    sel = decode_escapes(str(r.sample(q, 1)).strip("[]'").replace("\\n", "").strip('"'))
    bot.msg(sel, chan)
    mm.close()


def join(bot, chan: str, name: str, message: str) -> None:
    if name.lower() in bot.adminnames:
        newchan = message.split(" ", 1)[1].strip()
        bot.join(newchan, chan)


def eball(bot, chan: str, name: str, message: str) -> None:
    if message.endswith("?"):
        eb = open("eightball.txt", "r")
        q = eb.readlines()
        sel = str(r.sample(q, 1)).strip("[]'").replace("\\n", "").strip('"')
        bot.msg(f"The magic eightball says: {sel}", chan)
        eb.close()
    else:
        bot.msg("Please pose a Yes or No question.", chan)


def debug(bot, chan: str, name: str, message: str) -> None:
    if name.lower() in bot.adminnames:
        bot.msg(f"[DEBUG] NICKLEN={bot.nicklen}", chan)
        bot.msg(f"[DEBUG] ADMINS={bot.adminnames}", chan)
        bot.msg(f"[DEBUG] CHANNELS={bot.channels}", chan)


def raw(bot, chan: str, name: str, message: str) -> None:
    sendraw(message.split(" ", 1)[1])


def reboot(bot, chan: str, name: str, message: str) -> None:
    if name.lower() in bot.adminnames:
        bot.send("QUIT :Rebooting\n")
        bot.exit("Reboot")


def sudo(bot, chan: str, name: str, message: str) -> None:
    if name.lower() in bot.adminnames:
        bot.msg("Error - system failure, contact system operator", chan)
    elif "bot" in name.lower():
        bot.log("lol, no.")
    else:
        bot.msg("Access Denied", chan)


def nowplaying(bot, chan: str, name: str, message: str) -> None:
    if name in bot.npallowed:
        x02 = "\x02"
        bot.msg(
            f"f.sp {message.split(':')[1].split('(')[0].strip(f' {x02}')}",
            chan,
        )


data = {
    "!botlist": {"prefix": False, "aliases": []},
    "bugs bugs bugs": {"prefix": False, "aliases": []},
    "hi $BOTNICK": {"prefix": False, "aliases": ["hello $BOTNICK"]},
#   [npbase, su]
    "restart": {"prefix": True, "aliases": ["reboot"]},
    "uptime": {"prefix": True, "aliases": []},
    "raw ": {"prefix": True, "aliases": ["cmd "]},
    "debug": {"prefix": True, "aliases": ["dbg"]},
    "8ball": {"prefix": True, "aliases": ["eightball", "8b"]},
    "join ": {"prefix": True, "aliases": []},
    "quote": {"prefix": True, "aliases": ["q"]},
    "goat.mode.activate": {"prefix": True, "aliases": []},
    "goat.mode.deactivate": {"prefix": True, "aliases": []},
    "help": {"prefix": True, "aliases": []},
    "amIAdmin": {"prefix": True, "aliases": []},
    "ping": {"prefix": True, "aliases": []},
    "op me": {"prefix": False, "aliases": []},
}
checks = [npbase, su]
call = {
    "!botlist": botlist,
    "bugs bugs bugs": bugs,
    "hi $BOTNICK": hi,
    npbase: nowplaying,
    su: sudo,
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
    "amIAdmin": isAdmin,
    "ping": ping,
    "op me": op,
}
