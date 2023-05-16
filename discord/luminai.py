# Discord version of Luminai GPT chat bot

import os
import logging
import discord
from discord.ext import commands
from revChatGPT.V3 import Chatbot

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot_name = ""
bot_mention = ""

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

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

@bot.event
async def on_ready():
    global bot_name
    global bot_mention
    bot_name = bot.user.display_name
    bot_mention = f"<@{bot.user.id}>"

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    err = "We're experiencing exceptionally high demand. Please, try again."
    user = f"<@{message.author.id}>"
    prompt = f"{user} said: {message.content}"

    if isinstance(message.channel, discord.DMChannel):
        try:
            logging.info(prompt)
            send = chatbot.ask(prompt, "user", str(message.channel.id))
        except Exception as e:
            logging.debug(e)
            send = err
        await message.channel.send(send)
    else:
        if bot_mention in prompt:
            prompt = prompt.replace(bot_mention, bot_name)

            try:
                logging.info(prompt)
                send = chatbot.ask(prompt, "user", str(message.channel.id))
            except Exception as e:
                logging.debug(e)
                send = err

            await message.channel.send(send)
        else:
            try:
                logging.info(prompt)
                send = chatbot.ask(prompt, "user", str(message.channel.id))
                send = f"(hidden response): {send}"
            except Exception as e:
                logging.debug(e)
                send = err

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
