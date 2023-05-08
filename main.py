import discord
from discord.ext import commands, tasks
import requests
import sqlite3

conn = sqlite3.connect('pfp_data.db')

tkn = "ENTER-YOUR-BOT-TOKEN"
prefix = "ENTER-PREFIX"

client = commands.Bot(command_prefix=prefix,case_insensitive=True,intents=discord.Intents.all(),help_command=None)

conn.execute('CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY)')

@client.event
async def on_ready():
    channel_ids = get_channel_ids()
    for channel_id in channel_ids:
        send_pfp.start(channel_id)
    print('Bot is ready')

def get_channel_ids():
    cursor = conn.execute('SELECT id FROM channels')
    rows = cursor.fetchall()
    return [row[0] for row in rows]

@tasks.loop(seconds=5)
async def send_pfp(channel_id):
    response = requests.get('https://randomuser.me/api/')
    data = response.json()
    pfp_url = data['results'][0]['picture']['large']
    channel = client.get_channel(channel_id)
    embed = discord.Embed(title="Random PFP", color=0x2f3136)
    embed.set_footer(text=f"Made By @vent#1337")
    embed.set_image(url=pfp_url)
    await channel.send(embed=embed)
    print(f"[!] Sent PFP In Channel #{channel_id}")

# Can Only Be Used In 1 Guild & 1 channel, [ Multi Channel + Guild Feature Soon]
@client.command()
async def startpfp(ctx, channel_id: int = None):
    if channel_id is None:
        await ctx.send("> Please input a channel ID to send avatars!")
        return
    conn.execute('INSERT INTO channels (id) VALUES (?)', (channel_id,))
    conn.commit()
    send_pfp.start(channel_id)
    await ctx.send(f"> Started sending random avatars in <#{channel_id}>")


@client.command()
async def stoppfp(ctx):
    conn.execute('DELETE FROM channels')
    conn.commit()
    send_pfp.stop()
    await ctx.send('> Stopping Random Avatars.')

@client.command(aliases=['h'])
async def help(ctx):
    embed=discord.Embed(description="`.startpfp <channel_ID>` | `.stoppfp`")
    await ctx.send(embed=embed)

client.run(tkn)
