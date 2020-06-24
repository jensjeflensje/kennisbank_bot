import discord
import config
import requests
import asyncio
import time
from threading import Thread

client = discord.Client()

channels_data = {}


async def change_status():
    await client.wait_until_ready()
    while client.is_ready():
        await client.change_presence(activity=discord.Game(name=f"kennisbank.jederu.nl | {len(client.guilds)} guilds", type=1))
        await asyncio.sleep(20)


def fetch_channels():
    while True:
        r = requests.get("https://kennisbank.jederu.nl/api/channels/", params={"api_key": config.API_KEY})
        if r.status_code == 200:
            data = r.json()
            if data["success"]:
                global channels_data
                channels_data = data["data"]
        time.sleep(5)


@client.event
async def on_ready():
    print('KennisBank bot op account: {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    global channels_data
    try:
        guild_channels = channels_data[str(message.channel.guild.id)]
    except Exception as e:
        print(str(e))
        embed = discord.Embed(title="Error!", description="No config found for this server :(",
                              color=0xff0000)
        embed.set_footer(text="https://kennisbank.jederu.nl")
        await message.channel.send(embed=embed)
        return
    if message.channel.id in guild_channels:
        r = requests.get("https://kennisbank.jederu.nl/api/answer/", params={
            "api_key": config.API_KEY,
            "question": message.content,
            "guild": message.channel.guild.id,
        })
        error = ""
        if r.status_code == 200:
            data = r.json()
            if data["success"]:
                data = data["data"]
                embed = discord.Embed(title=data["question"], description=data["answer"],
                                      color=0x78C2AD)
                embed.set_footer(text="https://kennisbank.jederu.nl")
                await message.channel.send(embed=embed)
                return
            else:
                error = "Question not found :("
        else:
            error = "Whoops, something went wrong :("
        embed = discord.Embed(title="Error!", description=error,
                              color=0xff0000)
        embed.set_footer(text="https://kennisbank.jederu.nl")
        await message.channel.send(embed=embed)


client.loop.create_task(change_status())
Thread(target=fetch_channels).start()
client.run(config.TOKEN)
