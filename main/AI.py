from configs import CoT_PROMPT, CHAT_PROMPT, ROUTER_PROMPT, DEFAULT_PROMPT

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

        system_prompts= {
            "chat": CHAT_PROMPT,
            'router': ROUTER_PROMPT,
            "cot": CoT_PROMPT,
        }

        models = self.load_models()
        # print(models)
        if models is not None:
            for model in models:
                model["system_prompt"] = system_prompts.get(model['role'], DEFAULT_PROMPT)
                self.models[model["role"]] = Model(**model)
        else:
            print("🟥 NO MODELS FOUND exiting...")
            exit(1)

    async def generate(self, query):
        async def warm_up(name, model:Model):
            self.processes.append(subprocess.Popen(
                model.start_command, env=model.ollama_env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            ))
            await wait_until_ready(model.host)
            await model.generate_response("")
        
        for name, model in self.models.items():
            if not model.warmed_up: await warm_up(name, model)

        response = await self.models['router'].generate_response(query)
        response = response['response']
        response_json = json.loads(response)
        t = response_json['target']
        p = response_json['prompt']

        model = self.models[t]
        print(model.name)
        res = await model.generate_response(p)

        print(f"Target: {t}")
        print(f"Prompt: {p}")

        return f"{model.name}: "+res['response']

    async def shut_down(self):
        print("Shutting Down...")
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

async def main():
    ai = AI()
    while True:
        req = input(">>> ")
        if req == "/bye": break
        r = await ai.generate(req)
        print(r)
    await ai.shut_down()

if __name__ == "__main__":
    asyncio.run(main())  