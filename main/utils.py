import requests
from datetime import datetime
import asyncio
import json
from itertools import cycle
import colorama
import sys

colorama.init(True)

def save_memory():
    pass

def load_memory():
    pass

class Spinner:
    def __init__(self, text) -> None:
        self.done = asyncio.Event()
        self.text = text

    async def spinny_thingy(self, color = colorama.Fore.LIGHTCYAN_EX):
        chars = ["-", "\\", "|", '/']

        sys.stdout.write(" " * len(self.text) + '\r')
        while not self.done.is_set():
            for i in cycle(chars):
                if self.done.is_set():
                    break

                sys.stdout.write(f"{color}{self.text} {i}\r{colorama.Fore.RESET}")
                sys.stdout.flush()
                await asyncio.sleep(0.1)

            sys.stdout.write(" " * len(self.text) + '\r')

    def set_done(self):
        self.done.set()

    def change_text(self, new_text):
        self.text = new_text


async def main():
    done = asyncio.Event()
    s = Spinner("⚙️  Spinning up Pulse AI...")
    spinner_task = asyncio.create_task(s.spinny_thingy())

    from models import main as pulse_main

    await pulse_main()
    s.change_text("NEW")
    await pulse_main()

    s.set_done()
    await spinner_task
    print("✅ Spinny done!\n")

if __name__ == "__main__":
    asyncio.run(main())
