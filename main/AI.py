from configs import ( CoT_PROMPT, 
                     CHAT_PROMPT, 
                     ROUTER_PROMPT, 
                     DEFAULT_PROMPT, 
                     CHAOS_PROMPT, 
                     STREAM_DISABLED )

import asyncio
import subprocess
import aiohttp
import aiofiles
from models import Model
import json
from utils import save_memory, load_memory

# Sooo ... now what?

default_model = 'chat'

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

    async def init(self , auto_warmup = False):
        self.context = await self.load_context()
        if auto_warmup:
            await self.generate("", "discord", False)

    async def warm_up(self, model:Model):
            self.processes.append(subprocess.Popen(
                model.start_command, env=model.ollama_env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            ))
            await wait_until_ready(model.host)
            await model.generate_response("")

    async def generate(self, query:str, platform:str, save = True):
        for model in self.models.values():
            if not model.warmed_up: 
                await self.warm_up(model)

        stream = not (platform.lower() in STREAM_DISABLED)

        # Normal normal generation
        if query.startswith("!think"):
            query =  query.removeprefix("!think")
            model_name = "cot"
        elif query.startswith("!chat"):
            query = query.removeprefix("!chat")
            model_name = "chat"
            m = self.models[model_name]
            if m.system == CHAOS_PROMPT:
                m.system = CHAT_PROMPT
                print("Default Chat")
        elif query.startswith("!chaos"):
            query = query.removeprefix("!chaos")
            model_name = "chat"
            m = self.models[model_name]
            if m.system == CHAT_PROMPT:
                m.system = CHAOS_PROMPT
                print("Chaos Mode Activated")       
        else:
            model_name = default_model

        model = self.models[model_name]
        print(model.name)
        print(query)
        response = await model.generate_response(query, self.context, stream)
        response = response['response']
        if save:
            self.context['conversations'].extend([{"role":"user", "content": query}, {"role":"assistant", "content": response}]) # type: ignore

            await self.save_context()

        return response

    async def shut_down(self):
        print("Shutting Down...")
        for p in self.processes:
            p.terminate()
        for model in self.models.values():
            if model.session is not None:
                await model.session.close() # type: ignore

    async def load_context(self): 
        try:
            async with aiofiles.open(self.context_path) as file:
                content = await file.read()
                return json.loads(content)
        except FileNotFoundError:
            return {"conversations": []}
        except json.JSONDecodeError as e:
            print(f"🟥 JSON Error: {e}")
            return {"conversations": []}


    async def save_context(self):
        async with aiofiles.open(self.context_path, "w") as file:
            await file.write(json.dumps(self.context, indent=2))

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
    await ai.init() 
    while True:
        req = input(">>> ")
        if req == "/bye":
            await ai.shut_down()
            break
        r = await ai.generate(req, "discord")
        print(r)


if __name__ == "__main__":
    asyncio.run(main())  