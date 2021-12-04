import threading
import socket
import discord
import asyncio
from discord.ext.commands import Bot


class Terminal:
    bot: Bot
    guild: discord.Guild
    channel: discord.TextChannel

    def __init__(self, bot, loop):
        self.bot = bot
        self.loop = loop

    def run(self):
        while True:
            raw_in = input("> ")
            loop = asyncio.get_event_loop()
            info = asyncio.run_coroutine_threadsafe(self.say(905492845115351080, 914570080040407051, raw_in), loop)
            info.result()

    async def say(self, guild_id=905492845115351080, channel_id=914570080040407051, text=""):
        print("ran say")
        try:
            guild = await self.bot.fetch_guild(int(guild_id))
        except TypeError:
            print("invalid guild id")
            return
        try:
            channel = await guild.get_channel(int(channel_id))
        except TypeError:
            print("invalid channel id")
            return
        await channel.send(text)
        print("sent "+text)
