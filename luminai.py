import os
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from revChatGPT.V3 import Chatbot

app = App()

auth_test_response = app.client.auth_test()
bot_user_id = auth_test_response["user_id"]
user_info = app.client.users_info(user=bot_user_id)
bot_name = user_info['user']['real_name']
print(bot_user_id)
print(bot_name)

ChatGPTConfig = {
    "api_key": os.getenv("OPENAI_API_KEY")
}

if os.getenv("OPENAI_ENGINE"):
    ChatGPTConfig["engine"] = os.getenv("OPENAI_ENGINE")

if os.getenv("OPENAI_SYSTEM_PROMPT"):
    ChatGPTConfig["system_prompt"] = os.getenv("OPENAI_SYSTEM_PROMPT")

chatbot = Chatbot(**ChatGPTConfig)

@app.event("app_mention")
def handle_mention(event, say):
    prompt = event['text']
    try:
        response = chatbot.ask(prompt, "user", event['channel'])
        user = event['user']
        send = f"<@{user}> {response}"
    except Exception as e:
        print(e)
        send = "We're experiencing exceptionally high demand. Please, try again."

    # Use the `app.event` method to send a reply to the message thread
    original_message_ts = event["ts"]
    say(send, thread_ts=original_message_ts)

@app.event("message")
def handle_message_events(event, say):
    prompt = event['text']
    try:
        send = chatbot.ask(prompt, "user", event['channel'])
    except Exception as e:
        print(e)
        send = "We're experiencing exceptionally high demand. Please, try again."
    say(send)

@app.command("/reset")
def handle_some_command(ack, body, say):
    ack()
    prompt = body['text']
    if prompt:
        chatbot.reset(body['channel_id'], prompt)
        say(f"My programming was reset by <@{body['user_id']}> to '{prompt}'")
    else:
        chatbot.reset(body['channel_id'])
        say(f"My memory was reset by <@{body['user_id']}>")

# Start the app using Socket Mode with the app token
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
