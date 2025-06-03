import requests
from datetime import datetime
import json
from itertools import cycle

def save_memory():
    pass

def load_memory():
    pass

async def spinny_thingy(task):
    chars = ["-", "\\", "|", '/']

    done = False

    def spinny():
        for char in cycle(chars):
            if done:
                break

            print(f"{task} {char}",flush=True, end="\r")