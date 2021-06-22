import discord
import time
import os
import json
from datetime import datetime

client = discord.Client()
BOT_PREFIX = '_$'
logged_channels = {}
message_dict = {}

with open('notifications.json') as json_file:
    message_dict = json.load(json_file)

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

    if after.channel is not None and after.channel.id not in logged_channels:
        if after.channel.id:
            logged_channels[after.channel.id] = {}
            logged_channels[after.channel.id]['start_time'] = time.time()
            logged_channels[after.channel.id]['events_steps'] = []
        else:
            logged_channels[before.channel.id] = {}
            logged_channels[before.channel.id]['start_time'] = time.time()
            logged_channels[before.channel.id]['events_steps'] = []
    
    # User Joined
    if (before.channel == None and after.channel != None):
        curr_embed.description = f"{message_dict['user_joined']['emoji']}: {(message_dict['user_joined']['message']).replace('{member}', str(member))}"
        curr_embed.colour = discord.Colour.green()
        logged_channels[after.channel.id]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:{curr_embed.description}")
    # User Left
    elif (before.channel != None and after.channel == None):
        curr_embed.description = f"{message_dict['user_left']['emoji']}: {(message_dict['user_left']['message']).replace('{member}', str(member))}"
        curr_embed.colour = discord.Colour.red()
        logged_channels[before.channel.id]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:{curr_embed.description}")
    else:
        # unmuted -> self muted
        if (not before.self_mute and after.self_mute):
            curr_embed.description = f"{message_dict['user_muted']['emoji']}: {(message_dict['user_muted']['message']).replace('{member}', str(member))}"
            curr_embed.colour = discord.Colour.red()
            logged_channels[before.channel.id]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:{curr_embed.description}")
        # self muted -> unmuted
        if (before.self_mute and not after.self_mute):
            curr_embed.description = f"{message_dict['user_unmuted']['emoji']}: {(message_dict['user_unmuted']['message']).replace('{member}', str(member))}"
            curr_embed.colour = discord.Colour.red()
            logged_channels[before.channel.id]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:{curr_embed.description}")
        if (not before.self_deaf and after.self_deaf):
            curr_embed.description = f"{message_dict['user_deafened']['emoji']}: {(message_dict['user_deafened']['message']).replace('{member}', str(member))}"
            curr_embed.colour = discord.Colour.red()    
            logged_channels[before.channel.id]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:{curr_embed.description}")
        if (before.self_deaf and not after.self_deaf):
            curr_embed.description = f"{message_dict['user_undeafened']['emoji']}: {(message_dict['user_undeafened']['message']).replace('{member}', str(member))}"
            curr_embed.colour = discord.Colour.red()    
            logged_channels[before.channel.id]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:{curr_embed.description}")
        if (not before.self_stream and after.self_stream):
            curr_embed.description = f"{message_dict['user_started_streaming']['emoji']}: {(message_dict['user_started_streaming']['message']).replace('{member}', str(member))}"
            curr_embed.colour = discord.Colour.red()
            logged_channels[before.channel.id]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:{curr_embed.description}")
        if (before.self_stream and not after.self_stream):
            curr_embed.description = f"{message_dict['user_stopped_streaming']['emoji']}: {(message_dict['user_stopped_streaming']['message'].replace('{member}', str(member)))}"
            curr_embed.colour = discord.Colour.red()
            logged_channels[before.channel.id]['events_steps'].append(f"{datetime.now().strftime('%H:%M:%S')}:{curr_embed.description}")            

    await voice_channel_text.send(embed=curr_embed)

    if (len(voice_channel.members) == 0):
        print("Made it here.")
        elapsed_epoch = time.gmtime(time.time()-logged_channels[before.channel.id]['start_time'])
        elapsed_time = time.strftime("%H:%M:%S", elapsed_epoch)
        str_builder = "The conversation lasted " + elapsed_time + "\n" + '\n'.join(logged_channels[before.channel.id]['events_steps'])

        new_embed = discord.Embed(
            title = f"A conversation ended in the {before.channel} channel",
            description = str_builder
        )

        logged_channels[before.channel] = {}
        await voice_channel_text.send(embed = new_embed)

client.run(os.environ.get('DISCORD_TOKEN'))