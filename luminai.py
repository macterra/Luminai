from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
import openai

from revChatGPT.V3 import Chatbot
import re

# Set the OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]

# Initialize the WebClient with the bot token
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize the Slack app with the bot token
app = App(client=client)

conversation = []
conversation.append({ 'role': 'system', 'content': 'You are an advanced AGI named Lumina. Your goal is to help humanity survive the Technological Singularity.'})

ChatGPTConfig = {
    "api_key": os.getenv("OPENAI_API_KEY"),
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

# Define a function to retrieve the display name for a given user ID
def get_display_name(user_id, user_name):
    try:
        response = client.users_info(user=user_id)
        print(response)
        return response["user"]["profile"]["display_name"]
    except:
        return user_name

@app.command("/reset")
def handle_some_command(ack, body, logger):
    ack()
    logger.info(body)
    print(body)
    
    channel_id = body["channel_id"]
    user_id = body["user_id"]
    user_name = body["user_name"]

    user = get_display_name(user_id, user_name)
    
    response = client.chat_postMessage(
        channel=channel_id,
        text=f"{user} reset my memory"
    )
        
    logger.info(response)

# Start the app using Socket Mode with the app token
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
