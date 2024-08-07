#!/usr/bin/python3
from subprocess import run, PIPE
import config as conf
import random as r
from typing import Any, Callable
import bare, re, checks


def fpmp(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.msg("Firepup's master playlist", chan)
    bot.msg("https://open.spotify.com/playlist/4ctNy3O0rOwhhXIKyLvUZM", chan)


def version(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.msg("Version: " + bot.__version__, chan)


def goat(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.log("GOAT DETECTED")
    bot.msg("Hello Goat", chan)
    bot.gmode = False


def botlist(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.msg(
        f"Hi! I'm FireBot (https://git.amcforum.wiki/Firepup650/fire-ircbot)! {'My admins on this server are' + str(bot.adminnames) + '.' if bot.adminnames else ''}",  # pyright: ignore [reportOperatorIssue]
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
        f"{'Yes' if checks.admin(bot, name) else 'No'}",
        chan,
    )


def help(bot: bare.bot, chan: str, name: str, message: str) -> None:
    helpErr = False
    if bot.current == "bridge":
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
        if checks.admin(bot, name):
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
    qfilter = ""
    query = ""
    if " " in message:
        query = message.split(" ", 1)[1]
        qfilter = query.replace(
            " ", "\s"
        )  # pyright: ignore [reportInvalidStringEscapeSequence]
    r.seed()
    with open("mastermessages.txt", "r") as mm:
        q = []
        try:
            q = list(filter(lambda x: re.search(qfilter, x), mm.readlines()))
        except re.error:
            q = ["Sorry, your query is invalid regex. Please try again."]
        if q == []:
            q = [f'No results for "{query}" ']
        sel = conf.decode_escapes(
            r.sample(q, 1)[0].replace("\\n", "").replace("\n", "")
        )
        bot.msg(sel, chan)


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
        "ADMINS": str(bot.adminnames) + " (Does not include hostname checks)",
        "CHANNELS": bot.channels,
    }
    bot.msg(f"[DEBUG] {dbg_out}", chan)


def debugInternal(bot: bare.bot, chan: str, name: str, message: str) -> None:
    things = dir(bot)
    try:
        thing = message.split(" ", 1)[1]
    except IndexError:
        bot.msg("You can't just ask me to lookup nothing.", chan)
        return
    if thing in things:
        bot.msg(f"self.{thing} = {getattr(bot, thing)}", chan)
    else:
        bot.msg(f'I have nothing called "{thing}"', chan)


def debugEval(bot: bare.bot, chan: str, name: str, message: str) -> None:
    try:
        bot.msg(str(eval(message.split(" ", 1)[1])), chan)
    except Exception as E:
        bot.msg(f"Exception: {E}", chan)


def raw(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.sendraw(message.split(" ", 1)[1])


def reboot(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.send("QUIT :Rebooting\n")
    bot.exit("Reboot")


def sudo(bot: bare.bot, chan: str, name: str, message: str) -> None:
    if checks.admin(bot, name):
        bot.msg("Error - system failure, contact system operator", chan)
    elif "bot" in name.lower():
        bot.log("lol, no.")
    else:
        bot.msg("Access Denied", chan)


def nowplaying(bot: bare.bot, chan: str, name: str, message: str) -> None:
    if name in bot.npallowed and not bot.current == "bridge":
        x02 = "\x02"
        bot.msg(
            f"f.sp {message.split(x02)[1]}",
            chan,
        )


def fmpull(bot: bare.bot, chan: str, name: str, message: str) -> None:
    song = None
    try:
        song = bot.lastfmLink.get_user("Firepup650").get_now_playing()
    except:
        bot.msg(
            "Sorry, the music api isn't cooperating, please try again in a minute", chan
        )
    if song:
        bot.msg(
            "Firepup is currently listening to: " + song.__str__(),
            chan,
        )
    else:
        bot.msg("Firepup currently has his music stopped :/", chan)


def whoami(bot: bare.bot, chan: str, name: str, message: str) -> None:
    bot.msg(
        f"I think you are {name}{' (bridge)' if bot.current == 'bridge' else '@'+bot.tmpHost}",
        chan,
    )


def markov(bot: bare.bot, chan: str, name: str, message: str) -> None:
    word = None
    if " " in message:
        word = message.split()[1]
    proposed = bot.markov.generate_text(word)
    if proposed == word:
        proposed = f'Chain failed. (Firepup has never been recorded saying "{word}")'
    bot.msg(proposed, chan)


def setStatus(bot: bare.bot, chan: str, name: str, message: str) -> None:
    user, stat, reas = ("", 0, "")
    try:
        if message.split(" ")[1] == "help":
            bot.msg(
                "Assuming you want help with status codes. 1 is Available, 2 is Busy, 3 is Unavailable, anything else is Unknown.",
                chan,
            )
            return
        message = message.split(" ", 1)[1]
        user = message.split(" ")[0].lower()
        stat = int(message.split(" ")[1])
        reas = message.split(" ", 2)[2]
    except IndexError:
        bot.msg(
            f"Insufficent information to set a status. Only got {len(message.split(' ')) - (1 if '.sS' in message else 0)}/3 expected args.",
            chan,
        )
        return
    except ValueError:
        bot.msg("Status parameter must be an int.", chan)
        return
    match stat:
        case 1:
            stat = "Available"
        case 2:
            stat = "Busy"
        case 3:
            stat = "Unavailable"
        case _:
            stat = "Unknown"
    if user in ["me", "my", "I"]:
        user = "firepup"
    bot.statuses[user] = {"status": stat, "reason": reas}
    bot.msg(f"Status set for '{user}'. Raw data: {bot.statuses[user]}", chan)


def getStatus(bot: bare.bot, chan: str, name: str, message: str) -> None:
    user = ""
    try:
        user = message.split(" ")[1]
    except IndexError:
        user = "firepup"
    if bot.statuses.get(user) is None:
        bot.msg("You've gotta provide a nick I actually recognize.", chan)
        return
    bot.msg(
        f"{user}'s status: {'Unknown' if not bot.statuses[user].get('status') else bot.statuses[user]['status']} - {'Reason unset' if not bot.statuses[user].get('reason') else bot.statuses[user]['reason']}",
        chan,
    )


def check(bot: bare.bot, chan: str, name: str, message: str) -> None:
    try:
        msg = message.split(" ", 1)[1]
        nick = msg.split("!")[0]
        host = msg.split("@", 1)[1]
        cache = host in bot.dns
        dnsbl, raws = conf.dnsblHandler(bot, nick, host, chan)
        bot.msg(
            f"Blacklist check: {'(Cached) ' if cache else ''}{dnsbl if dnsbl else 'Safe.'} ({raws})",
            chan,
        )
    except IndexError:
        try:
            host = message.split(" ", 1)[1]
            cache = host in bot.dns
            dnsbl, raws = conf.dnsblHandler(
                bot, "thisusernameshouldbetoolongtoeveractuallybeinuse", host, chan
            )
            bot.msg(
                f"Blacklist check: {'(Cached) ' if cache else ''}{dnsbl if dnsbl else 'Safe.'} ({raws})",
                chan,
            )
        except Exception as E:
            bot.msg("Blacklist Lookup Failed. Error recorded to bot logs.", chan)
            bot.log(str(E), "FATAL")
    except Exception as E:
        bot.msg("Blacklist lookup failed. Error recorded to bot logs.", chan)
        bot.log(str(E), "FATAL")


def slap(bot: bare.bot, chan: str, name: str, message: str) -> None:
    msg = message.split(" ")
    if len(msg) > 1:
        msg = " ".join(msg[1:]).strip()
        if msg == bot.nick or not msg:
            msg = name
    else:
        msg = name
    bot.msg(f"\x01ACTION slaps {msg} around a bit with {r.choice(['a firewall', 'a fireball', 'a large trout', 'a computer', 'an rpi4', 'an rpi5', 'firepi', name])}\x01", chan)


data: dict[str, dict[str, Any]] = {
    "!botlist": {"prefix": False, "aliases": []},
    "bugs bugs bugs": {"prefix": False, "aliases": []},
    "hi $BOTNICK": {"prefix": False, "aliases": ["hello $BOTNICK"]},
    #   [npbase, su]
    "restart": {
        "prefix": True,
        "aliases": ["reboot", "stop", "hardreload", "hr"],
        "check": checks.admin,
    },
    "uptime": {"prefix": True, "aliases": []},
    "raw": {"prefix": True, "aliases": ["cmd "], "check": checks.admin},
    "debug": {"prefix": True, "aliases": ["dbg", "d"], "check": checks.admin},
    "debugInternal": {
        "prefix": True,
        "aliases": ["dbgInt", "dI"],
        "check": checks.admin,
    },
    "debugEval": {"prefix": True, "aliases": ["dbgEval", "dE"], "check": checks.admin},
    "8ball": {"prefix": True, "aliases": ["eightball", "8b"]},
    "join": {"prefix": True, "aliases": ["j"], "check": checks.admin},
    "quote": {"prefix": True, "aliases": ["q"]},
    "goat.mode.activate": {"prefix": True, "aliases": ["g.m.a"], "check": checks.admin},
    "goat.mode.deactivate": {
        "prefix": True,
        "aliases": ["g.m.d"],
        "check": checks.admin,
    },
    "help": {"prefix": True, "aliases": ["?"]},
    "amiadmin": {"prefix": True, "aliases": []},
    "ping": {"prefix": True, "aliases": []},
    "op me": {"prefix": False, "aliases": [], "check": checks.admin},
    "whoami": {"prefix": True, "aliases": []},
    "fpmp": {"prefix": True, "aliases": []},
    "version": {"prefix": True, "aliases": ["ver", "v"]},
    "np": {"prefix": True, "aliases": []},
    "markov": {"prefix": True, "aliases": ["m"]},
    "setStatus": {"prefix": True, "aliases": ["sS"], "check": checks.admin},
    "getStatus": {"prefix": True, "aliases": ["gS"]},
    "check": {"prefix": True, "aliases": [], "check": checks.admin},
    "slap": {"prefix": True, "aliases": ["s"]}
}
regexes: list[str] = [conf.npbase, conf.su]
call: dict[str, Callable[[bare.bot, str, str, str], None]] = {
    "!botlist": botlist,
    "bugs bugs bugs": bugs,
    "hi $BOTNICK": hi,
    conf.npbase: nowplaying,
    conf.su: sudo,
    "restart": reboot,
    "uptime": uptime,
    "raw": raw,
    "debug": debug,
    "debugInternal": debugInternal,
    "debugEval": debugEval,
    "8ball": eball,
    "join": join,
    "quote": quote,
    "goat.mode.activate": goatOn,
    "goat.mode.decativate": goatOff,
    "help": help,
    "amiadmin": isAdmin,
    "ping": ping,
    "op me": op,
    "whoami": whoami,
    "fpmp": fpmp,
    "version": version,
    "np": fmpull,
    "markov": markov,
    "setStatus": setStatus,
    "getStatus": getStatus,
    "check": check,
    "slap": slap,
}
