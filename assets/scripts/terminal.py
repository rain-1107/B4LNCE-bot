from threading import Thread
import socket
import discord
import asyncio
from discord.ext.commands import Bot


class Terminal:
    bot: Bot
    guild: discord.Guild
    channel: discord.TextChannel

    def __init__(self, bot):
        self.bot = bot
        self.loop = asyncio.new_event_loop()

    def run(self):
        Thread(target=self._thread).start()

    def _thread(self):
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.forever())
        self.loop.run_forever()

    async def forever(self):
        while True:
            raw_in = input("> ")
            await self.say(text=raw_in)

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
