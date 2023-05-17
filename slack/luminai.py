import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from revChatGPT.V3 import Chatbot

app = App()

auth_test_response = app.client.auth_test()
bot_user_id = auth_test_response["user_id"]
bot_mention = f"<@{bot_user_id}>"
user_info = app.client.users_info(user=bot_user_id)
bot_name = user_info['user']['real_name']

logging.basicConfig(level=logging.INFO)
print(f"bot user id: {bot_user_id}")
print(f"bot name: {bot_name}")

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

@app.event("message")
def handle_message_events(event, say, logger):
    logger.info(event)
    prompt = event['text']
    channel_type = event['channel_type']

    if channel_type == 'channel':
        if bot_mention in event["text"]:
            try:
                prompt = prompt.replace(bot_mention, bot_name)
                user = f"<@{event['user']}>"
                prompt = f"{user} said: {prompt}"
                logger.info(prompt)
                send = chatbot.ask(prompt, "user", event['channel'])
            except Exception as e:
                logger.debug(e)
                send = "We're experiencing exceptionally high demand. Please, try again."

            # Use the `app.event` method to send a reply to the message thread
            original_message_ts = event["ts"]
            say(send, thread_ts=original_message_ts)
            logger.info(send)
        else:
            try:
                user = f"<@{event['user']}>"
                prompt = f"{user} said: {prompt}"
                logger.info(prompt)
                send = chatbot.ask(prompt, "user", event['channel'])
            except Exception as e:
                logger.debug(e)
                send = "We're experiencing exceptionally high demand. Please, try again."
            logger.info(f"hidden response: {send}")

    if channel_type == 'im':
        try:
            logger.info(prompt)
            send = chatbot.ask(prompt, "user", event['channel'])
        except Exception as e:
            logger.debug(e)
            send = "We're experiencing exceptionally high demand. Please, try again."
        say(send)
        logger.info(send)

@app.command("/reset")
def handle_reset_command(ack, body, say, logger):
    ack()
    logger.info(body)
    prompt = body['text']
    if prompt:
        chatbot.reset(body['channel_id'], prompt)
        send = f"My programming was reset by <@{body['user_id']}> to '{prompt}'"
    else:
        chatbot.reset(body['channel_id'])
        send = f"My memory was reset by <@{body['user_id']}>"
    say(send)
    logger.info(send)

# Start the app using Socket Mode with the app token
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
