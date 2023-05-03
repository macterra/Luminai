# Luminai

Luminai is a ChatGPT slack bot

To run in a container, copy `sample.env` to `.env` and fill in the environment variables with your tokens and key. Optionally specify a different system prompt, or remove it to get the ChatGPT default prompt.

Start the bot with:
```
docker compose up -d
```

Since it uses websockets it doesn't need any exposted ports and can run anywhere with internet access.
