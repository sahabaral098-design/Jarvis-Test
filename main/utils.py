import requests
from datetime import datetime
import json
from itertools import cycle

def save_memory():
    pass

def load_memory():
    pass

async def spinny_thingy(tasks:list[str]):
    chars = ["-", "\\", "|", '/']

    done = False

    def spinny():
        for i in cycle(chars):
            if done:
                break

            print(f"{tasks}")

