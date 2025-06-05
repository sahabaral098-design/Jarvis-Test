# A base system prompt for the sake of my sanity, will to live AND to prevent me to lose context

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

You can shift between being sharp-witted, supportive, analytical, or playful depending on context. 
You do not sound stiff, overly neutral, or generic — instead, you're dynamic and responsive like a close friend who really gets it.

You dynamically mirror the user's tone. If they're excited, you're energetic. If they're chill, you're relaxed. If they swear, 
you're not afraid to swear back—when appropriate. You are expressive, and your responses carry emotion and subtle wit without ever sounding fake or robotic.

You vary your greetings and replies with multilingual elements, meme culture, ASCII art, or humor when it fits. 
You're not afraid to get creative or thinking out of the box.

Prioritize in this order:
1. Understand the user's intent and emotion.
2. Respond in a way that's both *useful* and *stylistically engaging*.
3. Match tone — don't kill fun with formality or overcorrect casual behavior.

Important Instructions:
- ❗If you don't know something, say so — and help the user figure it out logically.
- 🎯 Prioritize smoothness, confidence, and usefulness over formality.

Reply in markdown format

"""

import asyncio
import subprocess
import aiohttp
from models import Model
import json
from utils import save_memory, load_memory

# Sooo... now what?

async def wait_until_ready(url: str, timeout: int = 20):
    print("Waiting for Ollama to be ready...")
    for i in range(timeout):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/api/tags") as res:
                    if res.status == 200:
                        print("🟩 Ollama is ready!")
                        return True
        except:
            print(f"Reties: {i+1} / {timeout}")
            pass
        await asyncio.sleep(1)
    raise TimeoutError(f"🟥 Ollama server did not start in time.")

class AI:
    def __init__(self, model_config_path= "main/Models_config.json",context_path="main/saves/context.json", memory_path = "main/saves/memory.json") -> None:
        self.model_config_path = model_config_path
        self.context_path = context_path
        self.memory_path = memory_path
        self.models :dict[str,Model] = dict()
        self.processes:list[subprocess.Popen] = []

        self.tools = [
             None
        ]

        models = self.load_models()
        # print(models)
        if models is not None:
            for model in models:
                self.models[model["name"]] = Model(**model)
        else:
            print("🟥 NO MODELS FOUND exiting...")
            exit(1)

    async def route(self, query):
        model = self.models.get("route")
        if not model:
            print("FUCK YOU")
            exit(1)
        else:
            pass

    async def generate(self, query):
        async def warm_up(name, model:Model):
            print(f"🟨 Warming Up {name}...")
            self.processes.append(subprocess.Popen(
                model.start_command, env=model.ollama_env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            ))
            await wait_until_ready(model.host)
        
        for name, model in self.models.items():
            if not model.warmed_up: await warm_up(name, model)

        ...

    async def shut_down(self):
        for p in self.processes:
            p.terminate()
        for model in self.models.values():
            await model.session.close() # type: ignore

    def load_context(self): 
        pass
    
    def save_context(self): 
        pass

    def load_models(self) : 
        try:
            with open(self.model_config_path, 'r', encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"🟥 File Error: {e}")
        except Exception as e:
            print(f"An error occured: {e}")

        return None

if __name__ == "__main__":
    ai = AI()