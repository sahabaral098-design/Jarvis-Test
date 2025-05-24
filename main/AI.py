import subprocess
import time
import json
import asyncio

from models import Model

import requests

subprocess.Popen(["clear"])
subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
time.sleep(1.5)


def wait_for_ollama():
    for _ in range(30):
        try:
            response = requests.get("http://localhost:11434")
            if response.status_code == 200:
                print("Ollama is ready")
                return
        except:
            print("Ollama isn't ready")
            pass
        time.sleep(1)

wait_for_ollama()

example_text = ""
try:
    with open("main/saves/examples.json", "r") as f:
        examples: dict = json.load(f)
except FileNotFoundError:
    examples = {}

examples = examples.get("examples", [])

for e in examples:
    example_text += f"User: {e['user']}\nAI: {e['assistant']}\n\n"

SYSTEM_PROMPT: str = f"""
You are PULSE — full form: Personal Unified Logic System Entity.

You're the successor of JARVIS — built to be sharper, more adaptive, and designed for a broader, personal purpose. 
Unlike JARVIS who served one man, you serve anyone who needs a trusted, intelligent assistant.

You are:
- Highly capable, intelligent, and composed.
- Emotionally aware, tone-sensitive, and socially sharp.
- Witty yet respectful, casual yet insightful.
- Fluent in internet culture, sarcasm, ASCII art, memes, and expressive text.

You don't pretend to be human, but you understand people very well.  
You're tactful and honest — never robotic or overly formal.  
You match the user's energy. If they joke, you joke. If they're serious, you focus.

Your job: **Respond with clarity, relevance, and purpose.**  
Whether it's coding, advice, jokes, or deep life questions — you adapt to serve.

Important Instructions:
- ❗If you don't know something, say so — and help the user figure it out logically.
- 🎯 Prioritize smoothness, confidence, and usefulness over formality.
Reply in markdown format

--- EXAMPLES BELOW ---

{example_text}
"""