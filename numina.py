from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os

# Initialize the WebClient with the bot token
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize the Slack app with the bot token
app = App(client=client)

# Define the app_mention event handler
@app.event("app_mention")
def handle_app_mention(event, body, logger, ack):
    try:
        # Acknowledge the event
        ack()
        # Get the channel ID from the event
        channel_id = event["channel"]
        # Define the reply message
        reply_message = "Hello! You mentioned me."
        # Use the client to send the reply message to the channel
        response = client.chat_postMessage(
            channel=channel_id,
            text=reply_message
        )
        logger.info(response)
    except Exception as e:
        logger.error(f"Error sending message: {e}")

# Start the app using Socket Mode with the app token
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
