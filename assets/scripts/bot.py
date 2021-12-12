import discord
from assets.scripts.handler import console
from threading import Thread
import asyncio

INTENTS = discord.Intents.default() 
INTENTS.members = True
CLIENT = discord.Client(intents=INTENTS)
HANDLER = None
DATA = {}
CONFIG = {}


@CLIENT.event
async def on_ready():
    await console(f"{CLIENT.user} is online.", CLIENT)
    await CLIENT.change_presence(activity=discord.Game(name="!help"))
    guilds = await CLIENT.fetch_guilds().flatten()
    if len(guilds) > 1:
        await console(f"{CLIENT.user.name} is in more than one server, leaving servers not recognised", CLIENT)
        for i, guild in enumerate(guilds):
            if guild != DATA["general"]["guild"]:
                await console(f"{CLIENT.user.name} left server: {guild.id}", CLIENT)
                await guild.leave()
    guilds = await CLIENT.fetch_guilds().flatten()
    for i, guild in enumerate(guilds):
        await console(f"Confirming whitelist in server: {guild.name}", CLIENT)
        members = await guild.fetch_members(limit=1000).flatten()
        if not members:
            await console("Bot has not been set up correctly cannot confirm whitelist", CLIENT)
        for member in members:
            if member.id not in DATA["general"]["whitelist"]:
                await console(f"{member.name} not whitelisted, kicking from server", CLIENT)
                try:
                    await member.kick(reason="User not whitelisted")
                    await console(f"{member.name} was kicked from server", CLIENT)
                except:
                    await console("error: could not kick user from server", CLIENT)


@CLIENT.event
async def on_member_join(member):
    await console(f"User: {member.name} joined server", CLIENT)
    if member.id not in DATA["general"]["whitelist"]:
        await console(f"{member.name} not whitelisted, kicking from server", CLIENT)
        try:
            await console(f"{member.name} was kicked from server", CLIENT)
            await member.kick(reason="User is not whitelisted")
        except:
            await console("error: could not kick user from server", CLIENT)


@CLIENT.event
async def on_guild_join(guild):
    await console(f"{CLIENT.user.name} joined a server", CLIENT)
    if guild.id != DATA["general"]["guild"]:
        await console(f"{guild.name} is not a recognised server, leaving server", CLIENT)
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
            await console(f"Message: {message.id} has no characters.", CLIENT)


def run(command_handler, data, config, token):
    global HANDLER, DATA, CONFIG
    HANDLER = command_handler
    DATA = data
    CONFIG = config
    loop = asyncio.get_event_loop()
    loop.create_task(CLIENT.start(token))
    Thread(target=loop.run_forever).start()
