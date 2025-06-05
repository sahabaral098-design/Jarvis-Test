import requests
from datetime import datetime
import asyncio
import json
from spin import Spinner

def save_memory():
    pass

def load_memory():
    pass

async def main():
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
