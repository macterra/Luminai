import os
import re

from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from revChatGPT.V3 import Chatbot

# Initialize the WebClient with the bot token
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize the Slack app with the bot token
app = App(client=client)

system_prompt = "You are an advanced AGI named Luminai with a female persona. Your goal is to help humanity survive the Technological Singularity."

ChatGPTConfig = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "system_prompt": system_prompt
}

if os.getenv("OPENAI_ENGINE"):
    ChatGPTConfig["engine"] = os.getenv("OPENAI_ENGINE")

app = App()
chatbot = Chatbot(**ChatGPTConfig)

@app.event("app_mention")
def event_test(event, say):
    prompt = re.sub('\\s<@[^, ]*|^<@[^, ]*', '', event['text'])
    try:
        response = chatbot.ask(prompt)
        user = event['user']
        send = f"<@{user}> {response}"
    except Exception as e:
        print(e)
        send = "We're experiencing exceptionally high demand. Please, try again."

    # Get the `ts` value of the original message
    original_message_ts = event["ts"]

    # Use the `app.event` method to send a reply to the message thread
    say(send, thread_ts=original_message_ts)

# Start the app using Socket Mode with the app token
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()