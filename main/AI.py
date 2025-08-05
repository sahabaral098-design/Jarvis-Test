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

    async def init(self, platform:str, auto_warmup = False, ):
        self.context = await self.load_context()
        self.platform:str = platform
        if auto_warmup:
            async for _ in self.generate("", False):
                continue

    async def warm_up(self, model:Model):
            self.processes.append(subprocess.Popen(
                model.start_command, env=model.ollama_env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            ))
            await wait_until_ready(model.host)
            await model.generate_response_noStream("")

    async def route(self, query:str, manual = False):
        if manual:
            if query.startswith("!think"):
                return "cot"
            elif query.startswith("!chat"):
                self.models["chat"].system = CHAT_PROMPT
                return "chat"
            elif query.startswith("!chaos"):
                self.models["chat"].system = CHAOS_PROMPT
                print("chaos")
                return "chat"
            else:
                return default_model
            
        else:
            router = self.models.get("router")
            if router is None:
                print("🟥 Router model not found, using default model.")
                return default_model
            print("Routing query:", query)
            try:
                response = await router.generate_response_noStream(query, self.context)
                if response:
                    response = response.strip()
                    # response= json.loads(response)
                    print("Router response:", response)
                    if response in self.models.keys():
                        return response
                    else:
                        print(f"🟥 Router returned an unknown model: {response}, using default model.")
                        return default_model
            except Exception as e:
                print(f"🟥 Error during routing: {e}")
                return default_model

    async def generate(self, query:str, save = True):
        for model in self.models.values():
            if not model.warmed_up: 
                await self.warm_up(model)

        # Normal normal generation
        if query == "":
            return
        response = await self.route(query)
        print("router: " , response)
        if response:
            response = json.loads(response)
            model_name = response.get("target", default_model)
            query = response.get("prompt", query)
        else:
            model_name = default_model
        if model_name:
            model = self.models[model_name.lower()]
            print(model.name)
            print(query)

            stream = not (self.platform.lower() in STREAM_DISABLED)
            if not stream:
                response = await model.generate_response_noStream(query, self.context)
                if response:
                    response = response
                if save:
                    self.context['conversations'].extend([{"role":"user", "content": query}, {"role":"assistant", "content": response}]) # type: ignore
                    
                    await self.save_context()

                yield response
            else:
                part = ""
                response = part
                async for part in model.generate_response_Stream(query,self.context):
                    if part == "":
                        break
                    else:
                        response += part
                    yield part

                if save:       
                    self.context['conversations'].extend([
                        {"role": "user", "content": query},
                        {"role": "assistant", "content": response}
                    ])
                    await self.save_context()

    async def shut_down(self):
        print("Shutting Down...")
        for p in self.processes:
            p.terminate()
        for model in self.models.values():
            if model.session is not None:
                await model.session.close()
        
        await self.save_context()
        print("Done.")

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
    await ai.init("cli", True) 
    while True:
        req = input(">>> ")
        if req == "/bye":
            await ai.shut_down()
            break
        async for part in ai.generate(req,):
            print(part, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())  