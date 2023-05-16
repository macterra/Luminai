import os
import logging
import discord
from discord.ext import commands
from revChatGPT.V3 import Chatbot

intents = discord.Intents.default()  # Create an instance of the Intents class
bot = commands.Bot(command_prefix="!", intents=intents)  # Pass the Intents object to the Bot

ChatGPTConfig = {
    "api_key": os.getenv("OPENAI_API_KEY")
}

engine = os.getenv("OPENAI_ENGINE")
if engine:
    ChatGPTConfig["engine"] = engine
    print(f"using openai engine {engine}")

system_prompt = os.getenv("OPENAI_SYSTEM_PROMPT")
if system_prompt:
    system_prompt += "\nAll user names start with '<@' and end with '>'."
    ChatGPTConfig["system_prompt"] = system_prompt
    print(f"using system prompt [{system_prompt}]")

chatbot = Chatbot(**ChatGPTConfig)

logging.basicConfig(level=logging.INFO)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

    # bot.user.id will contain the bot's ID.
    print(f"My Bot's ID is: {bot.user.id}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    prompt = message.content

    print(message)

    try:
        #user = f"@{message.author.name}#{message.author.discriminator}"
        user = f"<@{message.author.id}>"
        prompt = f"{user} said: {prompt}"
        logging.info(prompt)
        send = chatbot.ask(prompt, "user", str(message.channel.id))
    except Exception as e:
        logging.debug(e)
        send = "We're experiencing exceptionally high demand. Please, try again."

    await message.channel.send(send)
    logging.info(send)

@bot.command(name='reset')
async def reset(ctx, *, prompt: str = None):
    if prompt:
        chatbot.reset(str(ctx.channel.id), prompt)
        send = f"My programming was reset by @{ctx.author.name}#{ctx.author.discriminator} to '{prompt}'"
    else:
        chatbot.reset(str(ctx.channel.id))
        send = f"My memory was reset by @{ctx.author.name}#{ctx.author.discriminator}"
    await ctx.send(send)
    logging.info(send)

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
