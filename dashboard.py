from flask import Flask
from dotenv import load_dotenv
import os
import base64

app = Flask(__name__)

load_dotenv()

token = os.getenv("DISCORD_BOT_TOKEN")
client_id = None
if token:
    try:
        first_part = token.split('.')[0]
        # Add padding if needed
        missing_padding = len(first_part) % 4
        if missing_padding:
            first_part += '=' * (4 - missing_padding)
        decoded = base64.b64decode(first_part)
        client_id = decoded.decode('utf-8')
    except:
        client_id = None

@app.route('/')
def dashboard():
    commands = [
        'nuke - Nukes the server by deleting channels, creating new ones, banning members, etc.',
        'banall - Bans all members in the server',
        'kickall - Kicks all members in the server',
        'roleall - Creates roles for all members',
        'channelall - Creates channels',
        'invite - Generates an invite link',
        'status - Shows bot status',
        'help - Shows help information',
        'addpremium - Adds a user to premium',
        'removepremium - Removes a user from premium',
        'bypassnuke - Bypasses protections and nukes',
        'slashbypassnuke - Slash command version of bypass nuke'
    ]

    # Placeholder for dynamic data - in a real implementation, this would fetch from the bot
    servers = "Connected to multiple servers (dynamic data not implemented yet)"
    status = "Online (assuming bot is running)"

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Apocalypse Control Center</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
                color: #fff;
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            header {{
                text-align: center;
                margin-bottom: 40px;
            }}
            h1 {{
                font-size: 3em;
                color: #ff4444;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                margin-bottom: 10px;
            }}
            .subtitle {{
                color: #ccc;
                font-size: 1.2em;
            }}
            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .card {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }}
            .card h2 {{
                color: #ff4444;
                margin-bottom: 15px;
                font-size: 1.5em;
            }}
            .status {{
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
            }}
            .status.online {{
                background: #4CAF50;
                color: white;
            }}
            .commands {{
                list-style: none;
            }}
            .commands li {{
                background: rgba(255, 255, 255, 0.1);
                margin: 5px 0;
                padding: 10px;
                border-radius: 5px;
                border-left: 4px solid #ff4444;
            }}
            .invite-btn {{
                display: inline-block;
                background: #ff4444;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 10px;
                transition: background 0.3s;
            }}
            .invite-btn:hover {{
                background: #cc3333;
            }}
            .note {{
                font-size: 0.8em;
                color: #ccc;
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>💀 Apocalypse Control Center</h1>
                <p class="subtitle">Command the chaos, unleash the apocalypse</p>
            </header>
            
            <div class="dashboard-grid">
                <div class="card">
                    <h2>📊 Status</h2>
                    <span class="status online">{status}</span>
                </div>
                
                <div class="card">
                    <h2>🏠 Servers</h2>
                    <p>{servers}</p>
                </div>
                
                <div class="card">
                    <h2>🤖 Invite Bot</h2>
                    <p>Add the bot to your Discord server</p>
                    {"<a href='https://discord.com/api/oauth2/authorize?client_id=" + str(client_id) + "&permissions=8&scope=bot' class='invite-btn' target='_blank'>Invite to Server</a>" if client_id else "<p class='note'>Set DISCORD_BOT_TOKEN in .env to enable invites</p>"}
                </div>
            </div>
            
            <div class="card">
                <h2>⚡ Available Commands</h2>
                <ul class="commands">
                    {"".join(f"<li>{cmd}</li>" for cmd in commands)}
                </ul>
            </div>
            
            <footer>
                <p>Built with 🔥 for maximum destruction</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    return html
    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)