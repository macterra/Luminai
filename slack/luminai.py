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

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

logging.info(f"bot user id: {bot_user_id}")
logging.info(f"bot name: {bot_name}")

ChatGPTConfig = {
    "api_key": os.getenv("OPENAI_API_KEY")
}

engine = os.getenv("OPENAI_ENGINE")
if engine:
    ChatGPTConfig["engine"] = engine
    logging.info(f"using openai engine {engine}")

system_prompt = os.getenv("OPENAI_SYSTEM_PROMPT")
if system_prompt:
    system_prompt += "\nAll user names start with '<@' and end with '>'."
    ChatGPTConfig["system_prompt"] = system_prompt
    logging.info(f"using system prompt [{system_prompt}]")

chatbot = Chatbot(**ChatGPTConfig)

@app.event("message")
def handle_message_events(event, say):
    logging.info(event)

    channel_type = event['channel_type']
    user = f"<@{event['user']}>"
    prompt = f"{user} said: {event['text']}"
    err = "We're experiencing exceptionally high demand. Please, try again."

    if channel_type == 'im':
        try:
            logging.info(prompt)
            send = chatbot.ask(prompt, "user", event['channel'])
        except Exception as e:
            logging.debug(e)
            send = err
        say(send)

    if channel_type == 'channel':
        if bot_mention in event["text"]:
            try:
                prompt = prompt.replace(bot_mention, bot_name)
                logging.info(prompt)
                send = chatbot.ask(prompt, "user", event['channel'])
            except Exception as e:
                logging.debug(e)
                send = err

            # Use the `app.event` method to send a reply to the message thread
            original_message_ts = event["ts"]
            say(send, thread_ts=original_message_ts)
        else:
            try:
                user = f"<@{event['user']}>"
                prompt = f"{user} said: {prompt}"
                logging.info(prompt)
                send = chatbot.ask(prompt, "user", event['channel'])
                send = f"(hidden response): {send}"
            except Exception as e:
                logging.debug(e)
                send = err

    logging.info(send)

@app.command("/reset")
def handle_reset_command(ack, body, say):
    ack()
    logging.info(body)
    prompt = body['text']
    if prompt:
        chatbot.reset(body['channel_id'], prompt)
        send = f"My programming was reset by <@{body['user_id']}> to '{prompt}'"
    else:
        chatbot.reset(body['channel_id'])
        send = f"My memory was reset by <@{body['user_id']}>"
    say(send)
    logging.info(send)

# Start the app using Socket Mode with the app token
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
