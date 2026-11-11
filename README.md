# MIMI618 Telegram Bot

First functional version of the MIMI618 Telegram bot.

Bot username: @MIMI618HunterBot

## Features

Commands currently implemented:

- /start
- /token
- /supply
- /contract
- /roadmap
- /links
- /community

The bot uses the Telegram Bot API through python-telegram-bot.

## Requirements

- Python 3.10+
- Telegram bot token from @BotFather

## Local setup

1. Create a virtual environment:

```bash
python -m venv .venv
```

2. Activate it.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set the Telegram token as an environment variable.

PowerShell:

```powershell
$env:TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
```

5. Optional project variables:

```powershell
$env:MIMI618_COMMUNITY_URL="https://t.me/YOUR_COMMUNITY"
$env:MIMI618_ROADMAP_URL="https://ton618-hunter.github.io/MimiToken/"
```

6. Run:

```bash
python bot.py
```

## Railway

The bot is designed for later Railway deployment.

Set `TELEGRAM_BOT_TOKEN` in Railway Variables. Do not put the real token into GitHub.

## Security

Never hardcode or commit the Telegram bot token.

## Scope

This version intentionally does not implement:

- trading
- wallet connection
- swaps
- buying/selling
- financial execution

Live on-chain supply, holders, wallet monitoring and TON618Hunter integration can be added later.
