# Discord version of Luminai GPT chat bot using OpenAI SDK

import os
import logging
import discord
from discord.ext import commands
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Init Discord bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot_name = ""
bot_mention = ""

# Init OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("Missing OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

engine = os.getenv("OPENAI_ENGINE", "gpt-4o")
logging.info(f"using OpenAI engine [{engine}]")
system_prompt = os.getenv("OPENAI_SYSTEM_PROMPT")
if system_prompt:
    system_prompt += "\nAll user names start with '<@' and end with '>'."
    logging.info(f"using system prompt [{system_prompt}]")
else:
    logging.info("no system prompt set")

def ask_openai(prompt: str):
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=engine,
            messages=messages,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.exception("OpenAI API error")
        return "We're experiencing exceptionally high demand. Please, try again."

@bot.event
async def on_ready():
    global bot_name
    global bot_mention
    bot_name = bot.user.display_name
    bot_mention = f"<@{bot.user.id}>"
    logging.info(f"Bot logged in as {bot_name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user = f"<@{message.author.id}>"
    prompt = f"{user} said: {message.content}"

    send = ""

    if isinstance(message.channel, discord.DMChannel):
        logging.info(prompt)
        send = ask_openai(prompt)
        await message.channel.send(send)

    elif bot_mention in message.content:
        prompt = prompt.replace(bot_mention, bot_name)
        logging.info(prompt)
        send = ask_openai(prompt)
        await message.channel.send(send)

    else:
        # Optional: hidden response logic for ambient messages
        logging.info(prompt)
        send = ask_openai(prompt)
        send = f"(hidden response): {send}"

    logging.info(send)

@bot.command(name='reset')
async def reset(ctx, *, prompt: str = None):
    if prompt:
        send = f"My programming was reset by @{ctx.author.name}#{ctx.author.discriminator} to '{prompt}', but note: I do not currently track memory."
    else:
        send = f"My memory was reset by @{ctx.author.name}#{ctx.author.discriminator}, but I am stateless in this version."
    await ctx.send(send)
    logging.info(send)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Missing DISCORD_TOKEN")
    bot.run(token)
