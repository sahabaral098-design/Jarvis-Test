import aiohttp
import json

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

        self.start_command = f"OLLAMA_HOST={self.host} ollama serve"
        
        self.warmed_up = False

    async def generate_response(self, query:str):
        url = f"{self.host}/api/chat" # For API calling
        headers = {"Content-Type": "application/json"}
        query = query if self.warmed_up else "hi"
        data = {
            "model": self.ollama_name,
            "messages": [{"role": "system", "content": self.system},{"role": "user", "content": query}],
            "stream": False,
        }
        try:
            if not self.warmed_up:
                print(f"{self.name}({self.ollama_name}) warming up...") # To prevent loading lag...
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                        response.raise_for_status()
                        await response.json()
                
                print(f"{self.name}({self.ollama_name}) warmed up!")
            else:
                print("Generating response...") # Normal generation
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, data=json.dumps(data)) as response:
                        response.raise_for_status()
                        
                        return await response.json()
                    
        except Exception as e:
            return f"An error occured: `{e}`"
