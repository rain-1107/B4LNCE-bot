import discord
import json
import sys
import random
from handler import is_admin, role_colour, console


INTENTS = discord.Intents.default() 
INTENTS.members = True
CLIENT = discord.Client(intents=INTENTS)
HANDLER = None

@CLIENT.event
async def on_ready():
    global BOT
    BOT = CLIENT.user
    await console(f"{BOT} is online.")
    await CLIENT.change_presence(activity=discord.Game(name="!help"))
    guilds = await CLIENT.fetch_guilds().flatten()
    if len(guilds) > 1:
        await console(f"{BOT.name} is in more than one server, leaving servers not recognised")
        for guild in guilds:
            if guild.id != DATA["general"]["guild"]:
                await console(f"{BOT.name} left server: {guild.id}")
                await guild.leave()
    guilds = await CLIENT.fetch_guilds().flatten()
    for guild in guilds:
        await console(f"Confirming whitelist in server: {guild.name}")
        members = await guild.fetch_members(limit=1000).flatten()
        if members == []:
            await console("Bot has not been set up correctly cannot confirm whitelist")
        for member in members:
            if member.id not in DATA["general"]["whitelist"]:
                await console(f"{member.name} not whitelisted, kicking from server")
                try:
                    await member.kick(reason="User not whitelisted")
                    await console(f"{member.name} was kicked from server")
                except:
                    await console("error: could not kick user from server")


@CLIENT.event
async def on_member_join(member):
    await console(f"User: {member.name} joined server")
    if member.id not in DATA["general"]["whitelist"]:
        await console(f"{member.name} not whitelisted, kicking from server")
        try:
            await console(f"{member.name} was kicked from server")
            await member.kick(reason="User is not whitelisted")
        except:
            await console("error: could not kick user from server")


@CLIENT.event
async def on_guild_join(guild):
    await console(f"{BOT.name} joined a server")
    if guild.id != DATA["general"]["guild"]:
        await console(f"{guild.name} is not a recognised server, leaving server")
        await guild.leave()


@CLIENT.event
async def on_message(message):
    if message.author != CLIENT.user:
        try:
            if message.content[0] == DATA["general"]["prefix"]:
                command = message.content[1:].split(" ")
                args = []
                if len(command) >= 2:
                    args = command[1:]
                await HANDLER.handle(command[0], message, *args)
        except IndexError:
            await console(f"Message: {message.id} has no characters.")


def run(command_handler):
    global HANDLER
    HANDLER = command_handler
    CLIENT.run(TOKEN)
