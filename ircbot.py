#!/usr/bin/python3
from bot import bot

server = args[1] if args else "UNSTABLE BOT MODE"


if __name__ == "__main__":
    instance = bot.bot(server)
    instance.mainloop()
