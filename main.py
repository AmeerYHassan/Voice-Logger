import discord
import time
import os
from datetime import datetime

client = discord.Client()
BOT_PREFIX = '_$'
logged_channels = {}

def get_curr_time():
    datetime.now().strftime("%H:%M:%S") + " " + time.tzname[0]

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith(BOT_PREFIX):
        await message.channel.send("Hello")
        print("A message has been sent")

@client.event
async def on_voice_state_update(member, before, after):
    global logged_channels
    voice_channel_text = client.get_channel(856020467995377674)
    voice_channel = client.get_channel(856016214597566479)

    curr_embed = discord.Embed(
        title=f"Update to the {after.channel} channel",
        description=f"There has been some sort of error."
    )

    if before.channel not in logged_channels:
        logged_channels[before.channel] = {}
        logged_channels[before.channel]['start_time'] = time.time()
        logged_channels[before.channel]['events_steps'] = []

    if (before.channel == None and after.channel != None):
        curr_embed.description = f":arrow_forward: {member} has joined the voice channel."
        curr_embed.colour = discord.Colour.green()
        logged_channels[after.channel]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:arrow_forward: {member} has joined the voice channel.")
    elif (before.channel != None and after.channel == None):
        curr_embed.description = f":arrow_backward: {member} has left the voice channel."
        curr_embed.colour = discord.Colour.red()
        logged_channels[before.channel]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:arrow_backward: {member} has left the voice channel.")
    else:
        if (after.self_mute):
            curr_embed.description = f":mute: {member} has muted themselves."
            curr_embed.colour = discord.Colour.red()
            logged_channels[before.channel]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:mute: {member} has muted themselves.")
        if (after.self_deaf):
            curr_embed.description = f":deaf_man: {member} has deafened themselves."
            curr_embed.colour = discord.Colour.red()    
            logged_channels[before.channel]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:deaf_man: {member} has deafened themselves.")
        if (after.self_stream):
            curr_embed.description = f":tv: {member} has started streaming."
            curr_embed.colour = discord.Colour.red()
            logged_channels[before.channel]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:tv: {member} has started streaming.")

    await voice_channel_text.send(embed=curr_embed)

    if (len(voice_channel.members) == 0):
        elapsed_epoch = time.gmtime(time.time()-logged_channels[before.channel]['start_time'])
        elapsed_time = time.strftime("%H:%M:%S", elapsed_epoch)
        str_builder = "The conversation lasted " + elapsed_time + "\n" + '\n'.join(logged_channels[before.channel]['events_steps'])

        new_embed = discord.Embed(
            title = f"A conversation ended in the {before.channel} channel",
            description = str_builder
        )
        await voice_channel_text.send(embed = new_embed)

client.run(os.environ.get('DISCORD_TOKEN'))