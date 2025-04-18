import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import openai
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Initialize Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])


# Identify the bot user and mention format
auth_test_response = app.client.auth_test()
bot_user_id = auth_test_response["user_id"]
bot_mention = f"<@{bot_user_id}>"
bot_name = app.client.users_info(user=bot_user_id)['user']['real_name']

logging.info(f"bot user id: {bot_user_id}")
logging.info(f"bot name: {bot_name}")

# Set up OpenAI API
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("Missing OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

# Load optional engine and system prompt
engine = os.getenv("OPENAI_ENGINE", "gpt-4")
logging.info(f"using engine [{engine}]")

system_prompt = os.getenv("OPENAI_SYSTEM_PROMPT")
if system_prompt:
    system_prompt += "\nAll user names start with '<@' and end with '>'."
    logging.info(f"using system prompt [{system_prompt}]")
else:
    logging.info("no system prompt set")

# Handler for all messages
@app.event("message")
def handle_message_events(event, say):
    logging.info(event)

    channel_type = event['channel_type']
    user = f"<@{event['user']}>"
    prompt = f"{user} said: {event['text']}"
    err = "We're experiencing exceptionally high demand. Please, try again."

    def get_response(prompt_text):
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt_text})

            response = client.chat.completions.create(
                model=engine,
                messages=messages,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.exception("OpenAI API call failed")
            return err

    send = ""

    if channel_type == 'im':
        logging.info(prompt)
        send = get_response(prompt)
        say(send)

    elif channel_type == 'channel':
        if bot_mention in event["text"]:
            prompt = prompt.replace(bot_mention, bot_name)
            logging.info(prompt)
            send = get_response(prompt)
            say(send, thread_ts=event["ts"])
        else:
            # (Optional) hidden response logic
            prompt = f"{user} said: {prompt}"
            logging.info(prompt)
            send = get_response(prompt)
            send = f"(hidden response): {send}"

    logging.info(send)

# Slash command to simulate memory reset
@app.command("/reset")
def handle_reset_command(ack, body, say):
    ack()
    logging.info(body)
    prompt = body['text']
    if prompt:
        send = f"My programming was reset by <@{body['user_id']}> to '{prompt}', but note: I do not currently track memory."
    else:
        send = f"My memory was reset by <@{body['user_id']}>, but I am stateless in this version."
    say(send)
    logging.info(send)

# Start app
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
