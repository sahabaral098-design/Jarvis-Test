import ollama 
import json

class Model:
    def __init__(self, name, ollama_name, context_path:str, system_prompt:str|None= None, tools= False, thinking= False) -> None:
        self.name = name
        self.ollama_name = ollama_name
        self.system = system_prompt
        self.has_tools = tools
        self.has_CoT = thinking

        self.context_path = context_path

        self.client = ollama.Client()

        self.async_client = ollama.AsyncClient()

    def pull(self, model):
        ollama.pull(model)
    def push(self, model):
        ollama.push(model)
    def delete(self, model):
        ollama.delete(model)
    
    async def warm_up(self, async_model = True):
        print(f"Warming up {self.name} ({self.ollama_name})...")
        message = [{'role': 'user', 'content': 'hi'}]
        if async_model:
            await self.async_client.chat(self.ollama_name, message)
        else:
            self.client.chat(self.ollama_name, message)
        print(f"{self.name} warmed up!")
    
    async def generate_response(self, query:str, user, async_client = True):
        if self.system is not None:
            messages = [{'role': "system", "content": self.system}, 
                    {"role":"user", "content": query}]

        print("Generating response...\n")
        response = ''
        thinking = None
        if async_client:
            async for part in await self.async_client.chat(model=self.ollama_name, messages=messages, stream=True):
                response += part['message']['content']
        else:
            response = self.client.chat(self.ollama_name)['message']['content']

        await self.save_context(user,query, response if response else "")
        if response:
            if "<think>" in response and "</think>" in response:
                thinking, response = response.split("</think>")
                thinking = thinking.replace("<think>", "").replace("</think>", "")
            else: 
                thinking= None
        return thinking, response
    
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
