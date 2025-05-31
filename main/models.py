import aiohttp
import json
import asyncio
import subprocess
import os # I hate my life; anyway this is for `env vars`

class Model:
    def __init__(self,role:str, name:str, ollama_name:str, has_tools:bool, has_CoT:bool, port:int, system_prompt:str) -> None:
        self.role = role
        self.name = name
        self.ollama_name = ollama_name
        self.has_tools = has_tools
        self.has_CoT = has_CoT
        self.port = port
        self.system = system_prompt

        self.host = f"http://localhost:{self.port}" # For seperate model loading

        self.start_command = ["ollama", "serve"]
        self.ollama_env = os.environ.copy()
        self.ollama_env["OLLAMA_HOST"] = self.host
        
        self.warmed_up = False

        self.session = None

    async def generate_response(self, query:str):
        url = f"{self.host}/api/chat" # For API calling
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.ollama_name,
            "messages": [{"role": "system", "content": self.system},{"role": "user", "content": query}],
            "stream": False,
        }

        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            if not self.warmed_up:
                print(f"🟨 [INFO] {self.name}({self.ollama_name}) warming up...")
                warmup_data = {
                    "model": self.ollama_name,
                    "messages": [{"role": "system", "content": self.system},{"role": "user", "content": "hi"}],
                    "stream": False,
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, data=json.dumps(warmup_data)) as response:
                        response.raise_for_status()
                        await response.json()
                
                self.warmed_up = True

                print(f"🟨 [INFO] {self.name}({self.ollama_name}) warmed up!")
                return {"response": ""}
                
            else:
                print("Generating response...") # Normal generation
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                        response.raise_for_status()

                        response = await response.json()

                        if 'message' in response and 'content' in response['message']:
                            return {"response": response['message']['content']}
                        else:
                            print(f"🟥 [Error]: Unexpected API response format: {response}")
                            return {"response": "An unexpected response format was received from the model."}
                    
        except aiohttp.ClientError as e:
            print(f"🟥 [ERROR] Connection error for {self.name}: {e}")
            return {"response": f"Connection error: {e}"}
        except json.JSONDecodeError:
            print(f"🟥 [JSON Decode Error for {self.name}]: Invalid JSON response.")
            return {"response": "Invalid JSON response from the model."}
        except Exception as e:
            print(f"🟥 [Generic Error for {self.name}]: {e}")
            return {"response": f"An unexpected error occurred: {e}"}


# ------- TEST -------

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


async def main(): # Testing
    m = Model("Testing", "Test", "llama3.2", True, False, 11434, "")
    subprocess.Popen(m.start_command, env=m.ollama_env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    await wait_until_ready(m.host) 

    if not  m.warmed_up: await m.generate_response("")
    for d in range(5):
        res = await m.generate_response(input(">>> "))
        print(res["response"])

    await m.session.close() # type: ignore


if __name__ == "__main__":

    asyncio.run(main())
