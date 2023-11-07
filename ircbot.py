#!/usr/bin/python3
from bot import bot
from sys import argv as args

server = args[1] if args else "UNSTABLE BOT MODE"


if __name__ == "__main__":
    instance = bot(server)
    instance.mainloop()
