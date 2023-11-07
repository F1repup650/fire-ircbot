#TODO: Finish this

def goat(bot, chan: str, name: str) -> None:
    bot.log("GOAT DETECTED")
    bot.msg("Hello Goat", chan)
    if mfind(
        message.lower(),
        ["!botlist"],
        False,
    ):
        sendmsg(
            f"Hi! I'm FireBot (https://git.amcforum.wiki/Firepup650/fire-ircbot)! My admins on this server are {adminnames}.",
            chan,
        )
    if mfind(
        message.lower(),
        ["bugs bugs bugs"],
        False,
    ):
        sendmsg(
            f"\x01ACTION realizes {name} looks like a bug, and squashes {name}\x01",
            chan,
        )
    if mfind(
        message.lower(),
        [f"hi {botnick.lower()}", f"hello {botnick.lower()}"],
        False,
    ):
        sendmsg(f"Hello {name}!", chan)
    elif (
        mfind(message, ["op me"], False) and name.lower() in adminnames
    ):
        op(name, chan)
    elif mfind(message, ["ping"]):
        sendmsg(
            f"{name}: pong",
            chan,
        )
    elif mfind(message, ["uptime"]):
        uptime = (
            run(["uptime", "-p"], stdout=PIPE).stdout.decode().strip()
        )
        sendmsg(
            f"Uptime: {uptime}",
            chan,
        )
    elif mfind(message, ["amIAdmin"]):
        sendmsg(
            f"{name.lower()} in {adminnames} == {name.lower() in adminnames}",
            chan,
        )
    elif mfind(message, ["help"]):
        if not helpErr:
            sendmsg("Command list needs rework", name)
            continue
            sendmsg("List of commands:", name)
            sendmsg(f'Current prefix is "{prefix}"', name)
            sendmsg(f"{prefix}help - Sends this help list", name)
            sendmsg(
                f"{prefix}quote - Sends a random firepup quote", name
            )
            sendmsg(
                f"{prefix}(eightball,8ball,8b) [question]? - Asks the magic eightball a question",
                name,
            )
            sendmsg(
                f"(hi,hello) {botnick} - The bot says hi to you", name
            )
            if name.lower() in adminnames:
                sendmsg(f"reboot {rebt} - Restarts the bot", name)
                sendmsg(exitcode + " - Shuts down the bot", name)
                sendmsg("op me - Makes the bot try to op you", name)
                sendmsg(
                    f"{prefix}join [channel(s)] - Joins the bot to the specified channel(s)",
                    name,
                )
        else:
            sendmsg("Sorry, I can't send help to bridged users.", chan)
    elif name.lower() in adminnames and mfind(
        message, ["goat.mode.activate"]
    ):
        log("GOAT DETECTION ACTIVATED", server)
        gmode = True
    elif name.lower() in adminnames and mfind(
        message, ["goat.mode.deactivate"]
    ):
        log("GOAT DETECTION DEACTIVATED", server)
        gmode = False
    elif mfind(message, ["quote"]):
        r.seed()
        mm = open("mastermessages.txt", "r")
        q = mm.readlines()
        sel = decode_escapes(
            str(r.sample(q, 1))
            .strip("[]'")
            .replace("\\n", "")
            .strip('"')
        )
        sendmsg(sel, chan)
        mm.close()
    elif mfind(message, ["join "]) and name.lower() in adminnames:
        newchan = message.split(" ")[1].strip()
        channels = joinchan(newchan, chan, channels)
    elif mfind(message, ["eightball", "8ball", "8b"]):
        if message.endswith("?"):
            eb = open("eightball.txt", "r")
            q = eb.readlines()
            sel = (
                str(r.sample(q, 1))
                .strip("[]'")
                .replace("\\n", "")
                .strip('"')
            )
            sendmsg(f"The magic eightball says: {sel}", chan)
            eb.close()
        else:
            sendmsg("Please pose a Yes or No question.", chan)
    elif (
        mfind(message, ["debug", "dbg"]) and name.lower() in adminnames
    ):
        sendmsg(f"[DEBUG] NICKLEN={nicklen}", chan)
        sendmsg(f"[DEBUG] ADMINS={adminnames}", chan)
        sendmsg(f"[DEBUG] CHANNELS={channels}", chan)
    elif (
        mfind(message, ["raw ", "cmd "]) and name.lower() in adminnames
    ):
        sendraw(message.split(" ", 1)[1])
    elif (
        mfind(message, [f"reboot {rebt}", f"reboot {gblrebt}"], False)
        or mfind(message, ["restart", "reboot"])
    ) and name.lower() in adminnames:
        send("QUIT :Rebooting\n")
        exit("Reboot")
    elif sucheck(message):
        if name.lower() in adminnames:
            sendmsg(
                "Error - system failure, contact system operator", chan
            )
        elif "bot" in name.lower():
            log("lol, no.", server)
        else:
            sendmsg("Access Denied", chan)
    elif np.search(message) and name in npallowed:
        x02 = "\x02"
        sendmsg(
            f"f.sp {message.split(':')[1].split('(')[0].strip(f' {x02}')}",
            chan,
        )
    elif len(message.split("\x01")) == 3:
        if not CTCPHandler(message, name):
            CTCP = message.split("\x01")[1]
            if CTCP == "ACTION ducks":
                sendmsg("\x01ACTION gets hit by a duck\x01", chan)
            elif CTCP.startswith("ACTION ducks"):
                sendmsg(
                    f"\x01ACTION gets hit by {CTCP.split(' ', 2)[2]}\x01",
                    chan,
                )
    if chan in channels and channels[chan] >= interval:
        r.seed()
        channels[chan] = 0
        mm = open("mastermessages.txt", "r")
        q = mm.readlines()
        sel = decode_escapes(
            str(r.sample(q, 1))
            .strip("[]'")
            .replace("\\n", "")
            .strip('"')
        )
        sendmsg(f"[QUOTE] {sel}", chan)
        mm.close()

data = {"!botlist": {"prefix": False, "aliases": []}, "bugs bugs bugs": {"prefix": False, "aliases": []}, "hi $BOTNICK": {"prefix": False, "aliases": ["hello $BOTNICK"]}, }
call = {"!botlist": botlist, "bugs bugs bugs": bugs, "hi $BOTNICK": hi, }
