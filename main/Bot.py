import discord
import os

DISCORD_KEY = os.getenv("DISCORD_KEY", "")

intents = discord.Intents.default()
intents.message_content = True


class Bot(discord.Client):
    async def on_ready(self):

        print(f'Logged in as {self.user}')

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        # print(f"{message.author.display_name } ({message.author}): {message.content}")
        think = None

        att = message.attachments
        add = ""
        if att:
            for a in att:
                    print(a.filename)
                    if a.filename.split(".")[-1] in ['py', 'txt']:
                        print("file detected")
                        c = await a.read()
                        decoded = c.decode(errors="ignore")
                        add = f"(user sent a file which reads:\n{decoded})"


        query:str = (add + "\n" + message.content).strip()
        if not query:
            return
        await message.channel.typing()
        try:
            think, response = ""
            await message.channel.typing()

        except Exception as e:
            print(f"[Error] {e}")
            response = f"Oops! Something went wrong. Try again later. (`{e}`)"

        await message.reply(response)
        if think is not None:
            await message.channel.send(f'Thinking:\n```\n{think}```')
        else: # Debuger
            await message.channel.send("-# NO THINKING")
        # print("AI: " + response)


bot = Bot(intents=intents)
bot.run(DISCORD_KEY)