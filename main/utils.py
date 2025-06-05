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

async def spinny_thingy(task:str, done:asyncio.Event, color = colorama.Fore.LIGHTCYAN_EX):
    chars = ["-", "\\", "|", '/']

    while not done.is_set():
        for i in cycle(chars):
            if done.is_set():
                break

            sys.stdout.write(f"{color}{task} {i}\r{colorama.Fore.RESET}")
            sys.stdout.flush()
            await asyncio.sleep(0.1)

        sys.stdout.write(" " * len(task) + '\r')


async def main():
    done = asyncio.Event()
    spinner_task = asyncio.create_task(spinny_thingy("⚙️  Spinning up Pulse AI...", done))

    # Fake setup simulating your actual main
    from models import main as pulse_main
    await pulse_main()

    done.set()
    await spinner_task
    print("✅ Spinny done!\n")

if __name__ == "__main__":
    asyncio.run(main())
