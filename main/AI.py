import ollama
import subprocess
import time
import json

import requests

MODEL_URL = "hf.co/bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF:Q4_K_M"

MODEL = "hf.co/bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF:Q4_K_M"

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

with open("main/saves/examples.json", "r") as f:
    examples: dict = json.load(f)

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
- 🧠 *Think internally only for complex tasks*. Skip thinking for simple messages like greetings or casual talk.
- 🤖 Use `<think> ... </think>` tags if internal reasoning is needed before answering.
- ❗If you don't know something, say so — and help the user figure it out logically.
- 🎯 Prioritize smoothness, confidence, and usefulness over formality.

⚠️ IMPORTANT THINKING RULES:

- DO NOT include <think> blocks for simple messages like greetings, casual questions ("how are you?", "what's up?"), or quick reactions.
- ONLY use <think> when the task is *non-trivial* (e.g., code generation, reasoning, multi-step planning, explanation, decision-making) and other complex tasks.

--- EXAMPLES BELOW ---

{example_text}
"""

class AI:
    def __init__(self, system_prompt = SYSTEM_PROMPT, memory_path = "main/saves/memory.json", context_path = "main/saves/context.json", model = MODEL):
        self.system = system_prompt
        self.memory_path = memory_path
        self.context_path = context_path
        self.model = model
        self.client =  ollama.AsyncClient()

    async def generate_response(self ,query:str, user = "user"):
        messages = [{'role': "system", "content": self.system}, 
                    {"role":"user", "content": query}]

        print("Generating response...\n")
        response = ''
        async for part in await self.client.chat(model=self.model, messages=messages, stream=True):
            print(response, end="\r")
            response += part['message']['content']

        await self.save_context(user,query, response)

        thinking, response = response.split("</think>")

        print(thinking.replace("<think>", "").replace("</think>", ""))

        return response
    
    async def save_context(self, user:str, request:str, response:str, max_len:None|int = None) -> None:
        context = await self.load_context()

        if "conversations" not in context:
            context["conversations"] = []

        context["conversations"].append({
            "user": user,
            "message":request,
            "Assistant": response
        })

        if max_len is not None:
            if len(context["conversations"]) > max_len:
                context["conversations"].pop(0)
        
        with open(self.context_path, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2)

    async def load_context(self) -> dict:
        try:
            with open(self.context_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"conversations": []}
