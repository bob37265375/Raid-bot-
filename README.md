# Raid-bot-
Raids people servers

## Setup
1. Install dependencies: The virtual environment is already configured.
2. Add your Discord bot token to `.env`: `DISCORD_BOT_TOKEN=your_token_here`
3. Run the bot: `/workspaces/Raid-bot-/.venv/bin/python main.py`
4. Run the dashboard: `/workspaces/Raid-bot-/.venv/bin/python dashboard.py` (access at http://localhost:8080)

## Dashboard
The dashboard shows:
- Bot status
- Connected servers
- Available commands

## Deploying the Dashboard Publicly
To make the dashboard accessible to anyone, deploy it to a cloud platform:

### Option 1: Railway (Recommended - Easiest)
1. Go to [Railway.app](https://railway.app) and sign up
2. Create a new project and connect your GitHub repo
3. Add environment variable: `DISCORD_BOT_TOKEN=your_token_here`
4. Railway will auto-deploy the Flask app
5. Your dashboard will be live at a URL like `https://your-app.railway.app`

### Option 2: Render
1. Go to [Render.com](https://render.com) and sign up
2. Create a new Web Service
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python dashboard.py`
6. Add environment variable: `DISCORD_BOT_TOKEN=your_token_here`
7. Deploy and get your public URL

### Option 3: Heroku
1. Install Heroku CLI
2. `heroku create`
3. `git push heroku main`
4. Set env var: `heroku config:set DISCORD_BOT_TOKEN=your_token_here`

The dashboard will be publicly accessible and anyone can view the bot's status and commands!
