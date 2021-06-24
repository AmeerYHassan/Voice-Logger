import discord
from discord.ext import commands
from discord_slash import SlashCommand
import DiscordUtils
import db
import time
import os
import json
from datetime import datetime

client = discord.Client()
secrets = json.load(open('secrets.json'))
logged_channels = {}
guild_text_dict = {}
message_dict = {}

slash = SlashCommand(client, sync_commands=True)
verbosity = False

with open('notifications.json') as json_file:
    message_dict = json.load(json_file)

def get_curr_time():
    return (datetime.now().strftime("%H:%M:%S") + " " + time.tzname[0])

def generate_message(message_type, member_name):
    global message_dict

    return f"{message_dict[message_type]['emoji']} {(message_dict[message_type]['message']).replace('{member}', '**'+str(member_name)+'**')}"

# Bot Functions #
@slash.slash(description="Set the voice channel to monitor and the text channel to send messages to")
async def set_channel(ctx, text_channel_name):
    print(text_channel_name)
    try:
        text_channel = discord.utils.get(ctx.guild.channels, name=text_channel_name)
        db.set_text_channel_id(ctx.guild.id, text_channel.id)
        await ctx.send(f"The text channel has been set to the **{text_channel}** text chat")
    except Exception as e:
        print(e)
        await ctx.send(f"{text_channel_name} channel was not found.")

@slash.slash(description="The verbosity toggle: type 'y' if you want every voice chat change announced, type 'n' otherwise.")
async def verbosity(ctx, verbosity_state):
    global verbosity

    if (verbosity_state.lower() == "y"):
        db.set_verbosity(ctx.guild.id, True)
        await ctx.send(f"Verbosity has been turned on")
    elif (verbosity_state.lower() == "n"):
        db.set_verbosity(ctx.guild.id, False)
        await ctx.send(f"Verbosity has been turned off")
    else:
        await ctx.send(f"Please read the command description correctly.")

@slash.slash(description="View history of voice chats.")
async def vc_history(ctx):
    vc_history = db.get_vc_history(ctx.guild.id)
    embed_list = []

    for count, curr in enumerate(vc_history):
        start_date = datetime.fromtimestamp(curr['start_time']).strftime("%m/%d/%y %I:%M:%S %p")
        end_date = datetime.fromtimestamp(curr['end_time']).strftime("%m/%d/%y %I:%M:%S %p")

        embed = discord.Embed(
            title = f"{count+1}: Conversation in {curr['channel_name']}",
            description = "From **" + start_date + "** to **" + end_date + "**\n" + '\n'.join(curr["history"]),
            color=discord.Colour.blue()
        )

        embed_list.append(embed)

    paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
    paginator.add_reaction('⏮️', "first")
    paginator.add_reaction('⏪', "back")
    paginator.add_reaction('🔐', "lock")
    paginator.add_reaction('⏩', "next")
    paginator.add_reaction('⏭️', "last")
    await paginator.run(embed_list)

@client.event
async def on_guild_join(guild):
    if(not db.check_in_db(guild.id)):
        db.create_guild_document(guild.id, guild.name)

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

@client.event
async def on_voice_state_update(member, before, after):
    global logged_channels

    voice_channel = None

    if (member.guild.id not in guild_text_dict):
        mem_text_channel_id = db.get_text_channel_id(member.guild.id)
        guild_text_dict[member.guild.id] = {}
        if (mem_text_channel_id == -1):
            return
        guild_text_dict[member.guild.id]["text_id"] = mem_text_channel_id
        guild_text_dict[member.guild.id]["verbosity"] = db.get_verbosity(member.guild.id)
    
    text_channel_id = guild_text_dict[member.guild.id]["text_id"]

    if (before.channel is not None):
        voice_channel = client.get_channel(before.channel.id)
    elif (after.channel is not None):
        voice_channel = client.get_channel(after.channel.id)

    voice_channel_text = client.get_channel(text_channel_id)

    curr_embed = discord.Embed(
        title=f"Update to the {after.channel} channel",
        description=f"There has been some sort of error."
    )

    if after.channel is not None and after.channel.id not in logged_channels:
        logged_channels[after.channel.id] = {}
        logged_channels[after.channel.id]['start_time'] = time.time()
        logged_channels[after.channel.id]['events_steps'] = []
        logged_channels[after.channel.id]['user_list'] = {}
    
    # User Joined
    if (before.channel == None and after.channel != None):
        curr_embed.description = generate_message('user_joined', member)
        curr_embed.colour = discord.Colour.green()
        logged_channels[after.channel.id]['user_list'][str(member)] = time.time()
        logged_channels[after.channel.id]['events_steps'].append(f"`{get_curr_time()}` ├ {curr_embed.description}")
    # User Left
    elif (before.channel != None and after.channel == None):
        elapsed_epoch_int = time.time()-logged_channels[before.channel.id]['user_list'][str(member)]
        elapsed_epoch = time.gmtime(elapsed_epoch_int)
        elapsed_time = time.strftime('%H:%M:%S', elapsed_epoch)
        curr_embed.description = generate_message('user_left', member)
        curr_embed.colour = discord.Colour.red()
        logged_channels[before.channel.id]['events_steps'].append(f"`{get_curr_time()}` ├ {curr_embed.description}, `{elapsed_time}`")
        db.update_user_time(member.guild.id, member.id, elapsed_epoch_int)
    else:
        # unmuted -> self muted
        if (not before.self_mute and after.self_mute):
            curr_embed.description = generate_message('user_muted', member)
            curr_embed.colour = discord.Colour.red()
            logged_channels[before.channel.id]['events_steps'].append(f"`{get_curr_time()}` ├ {curr_embed.description}")
        # self muted -> unmuted
        if (before.self_mute and not after.self_mute):
            curr_embed.description = generate_message('user_unmuted', member)
            curr_embed.colour = discord.Colour.red()
            logged_channels[before.channel.id]['events_steps'].append(f"`{get_curr_time()}` ├ {curr_embed.description}")
        # undeafened -> self deafened
        if (not before.self_deaf and after.self_deaf):
            curr_embed.description = generate_message('user_deafened', member)
            curr_embed.colour = discord.Colour.red()    
            logged_channels[before.channel.id]['events_steps'].append(f"`{get_curr_time()}` ├ {curr_embed.description}")
        # self deafened -> undeafened
        if (before.self_deaf and not after.self_deaf):
            curr_embed.description = generate_message('user_undeafened', member)
            curr_embed.colour = discord.Colour.red()    
            logged_channels[before.channel.id]['events_steps'].append(f"`{get_curr_time()}` ├ {curr_embed.description}")
        # not streaming -> streaming
        if (not before.self_stream and after.self_stream):
            curr_embed.description = generate_message('user_started_streaming', member)
            curr_embed.colour = discord.Colour.red()
            logged_channels[before.channel.id]['events_steps'].append(f"`{get_curr_time()}` ├ {curr_embed.description}")
        # streaming -> not streaming
        if (before.self_stream and not after.self_stream):
            curr_embed.description = generate_message('user_stopped_streaming', member)
            curr_embed.colour = discord.Colour.red()
            logged_channels[before.channel.id]['events_steps'].append(f"`{get_curr_time()}` ├ {curr_embed.description}")            

    if (guild_text_dict[member.guild.id]["verbosity"]):
        await voice_channel_text.send(embed=curr_embed)

    # If no one is in the voice channel... 
    if (len(voice_channel.members) == 0):
        end_time = time.time()
        elapsed_epoch = time.gmtime(end_time-logged_channels[before.channel.id]['start_time'])
        elapsed_time = time.strftime("%H:%M:%S", elapsed_epoch)
        str_builder = "The conversation lasted `" + elapsed_time + "`\n" + '\n'.join(logged_channels[before.channel.id]['events_steps'])

        voice_chat_post = {
            "start_time": logged_channels[before.channel.id]['start_time'],
            "end_time": end_time,
            "channel_name": voice_channel.name,
            "history": logged_channels[before.channel.id]['events_steps']
        }

        db.update_vc_history(member.guild.id, voice_chat_post)

        new_embed = discord.Embed(
            title = f"A conversation ended in the {before.channel} channel",
            description = str_builder
        )

        await voice_channel_text.send(embed = new_embed)
        del logged_channels[before.channel.id]
        del guild_text_dict[member.guild.id]

client.run(secrets["DISCORD_TOKEN"])