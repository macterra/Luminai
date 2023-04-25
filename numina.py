from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
import openai

# Set the OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]

# Initialize the WebClient with the bot token
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize the Slack app with the bot token
app = App(client=client)

conversation = []

# Define the app_mention event handler
@app.event("app_mention")
def handle_app_mention(event, body, logger, ack):
    try:
        print(event)

        # Acknowledge the event
        ack()

        # Get the channel ID from the event
        channel_id = event["channel"]
        message_text = event["text"]

        # Generate a response using the GPT-3 API
        response = openai.Completion.create(
            engine="davinci",
            prompt='You are an advanced AGI named Lumina. Your goal is to help humanity survive the Technological Singularity.\nSomeone says:  ' + message_text + '\n You response with:',
            max_tokens=100
        )

        print(response)

        # Extract the generated text from the GPT-3 API response
        gpt_response_text = response["choices"][0]["text"].strip()

        # Use the client to send the reply message to the channel
        response = client.chat_postMessage(
            channel=channel_id,
            text=gpt_response_text
        )
        logger.info(response)
    except Exception as e:
        logger.error(f"Error sending message: {e}")


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
