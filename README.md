# DiCsAI

DiCsAI is a tool for all businesses that use WhatsApp messages. It is a bot that uses AI to respond to messages automatically, without human intervention.

## Requirements

- Python 3.10+
- Groq account
- Meta Developer account

## Setup

```bash
git clone <repo url>
cd DiCsAI
pip install -r requirements.txt
```
Collaborators must copy `.env.example` to `.env` and fill in their own keys.

## Running

Start the bot:

```bash
python app.py
```

The server runs on `http://localhost:5000`.

Meta cannot reach `localhost`, so open a **second terminal** and expose the port:

```bash
ngrok http 5000
```

Copy the HTTPS URL that ngrok gives you and register `<that-url>/webhook` as the
callback URL in the Meta dashboard, using the same `VERIFY_TOKEN` from your `.env`.

