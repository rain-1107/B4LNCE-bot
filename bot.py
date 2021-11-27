import discord
import json
import sys

PATH = "assets/"
DATA_FILE = "custom_data.json"
CONFIG_FILE = "custom_config.json"

INTENTS = discord.Intents.default() 
INTENTS.members = True # This line breaks this script but is needed for whitelist check. Fix later.
CLIENT = discord.Client(intents=INTENTS)

with open(PATH + CONFIG_FILE, "r") as config:
    TOKEN = json.load(config)["token"]
if TOKEN == "Add bot token here":
    print("Add token to 'config.json'")
    sys.exit()

with open(PATH + DATA_FILE, "r") as data:
    DATA = json.load(data)


async def role_colour(message):
    roles = await message.guild.fetch_roles()
    highest = discord.utils.find(lambda role: role in roles,
                                 reversed(message.guild.get_member(CLIENT.user.id).roles))
    return highest.colour


async def console(str):
    print(str)
    if DATA["general"]["console"] != 0:
        guild = await CLIENT.fetch_guild(DATA["general"]["guild"])
        for channel in await guild.fetch_channels():
            if channel.id == int(DATA["general"]["console"]):
                await channel.send(str)
                return


def save():
    with open(PATH + DATA_FILE, "w") as data:
        json.dump(DATA, data, indent=2)


def is_admin(user: discord.User):
    for admin in DATA["general"]["admin_ids"]:
        if user.id == admin:
            return True
    return False


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
                    await console(f"{member.name} was kicked from server")
                    await member.kick(reason="User not whitelisted")
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


class CommandHandle:
    def __init__(self):
        self.commands = {"ping": self.ping, "echo": self.echo, "help": self.help, "todo": self.todo, "exit": self.exit, "save": self.save ,"console": self.console}

    async def handle(self, command, *args):
        if command.lower() in self.commands:
            await self.commands[command.lower()](*args)

    async def help(self, message, *args):
        embed = discord.Embed(title="Help Menu", colour=await role_colour(message))
        if len(args) == 0:
            admin = False
            cmds = DATA["commands"]
        else:
            if args[0].lower() == "admin":
                admin = True
                if is_admin(message.author):
                    cmds = DATA["admin_commands"]
                    embed.title = "Admin Help Menu"
                else:
                    return
            else:
                admin = False
                cmds = DATA["commands"]
        for command in cmds:
            embed.add_field(name=DATA["general"]["prefix"]+command, value=cmds[command], inline=False)
        await console(f"User: {message.author} used help command (admin = {admin})")
        await message.channel.send(embed=embed)

    async def ping(self, message):
        embed = discord.Embed(title="Pong", colour=await role_colour(message))
        ping = round(CLIENT.latency * 1000)
        if ping > 100:
            desc = "Running pretty slow"
        else:
            desc = "I am speed"
        embed.add_field(name=str(ping) + " ms", value=desc, inline=True)
        await console(f"User: {message.author} used ping command (ping = {ping})")
        await message.channel.send(embed=embed)

    async def echo(self, message, *echo):
        send = ""
        for word in echo:
            send += word+" "
        if send != "":
            await message.channel.send(send)
            await console(f"User: {message.author} used echo command (echo = {send})")
        else:
            await console(f"User: {message.author} used echo command (error = no arguments passed))")

    async def todo(self, message, *args):
        if len(args) == 0:
            embed = discord.Embed(title="TODO", colour=await role_colour(message))
            list = DATA["todo"]
            if len(list) == 0:
                embed.add_field(name="Nothing in the TODO list.", value=f"Add something with {DATA['general']['prefix']}todo add")
            else:
                for i, todo in enumerate(DATA["todo"]):
                    embed.add_field(name=f"{i+1}.", value=todo, inline=False)
            await console(f"User: {message.author} used TODO command (todo = {DATA['todo']}))")
            await message.channel.send(embed=embed)

        elif args[0].lower() == "add":
            add = ""
            for word in args[1:]:
                add += word+" "
            add = add[:len(add)-1]
            DATA["todo"].append(add)
            await console(f"User: {message.author} used TODO add command (added = {add}))")
            await message.channel.send(f"Added '{add}' to the TODO list.")

        elif args[0].lower() == "remove":
            try:
                index = int(args[1])-1
                try:
                    removed = DATA["todo"].pop(index)
                except IndexError:
                    await console(f"User: {message.author} used TODO remove command (error = point did not exist))")
                    await message.channel.send("That number point does not exist.")
                    return
                await console(f"User: {message.author} used TODO remove command (removed = {removed}))")
                await message.channel.send(f"Removed '{removed}' from the TODO list.")
            except TypeError:
                await console(f"User: {message.author} used TODO remove command (error = argument was not passed))")
                await message.channel.send("Use a number to signify which point to remove.")
            except IndexError:
                await console(f"User: {message.author} used TODO remove command (error = no argument passed))")
                await message.channel.send("Add a number to signify which point to remove.")

        elif args[0].lower() == "search":
            if len(args) == 1:
                await console(f"User: {message.author} used TODO search command (error = no arguments passed))")
                await message.channel.send("Please search for something.")
                return
            else:
                search = ""
                for word in args[1:]:
                    search += word.lower() + " "
                search = search[:len(search)-1]
                matches = []
                for i, point in enumerate(DATA["todo"]):
                    if search in point.lower():
                        matches.append(i)
                s = ""
                if len(matches) != 1: s = "s"
                embed = discord.Embed(title=f"{len(matches)} Result{s}", colour=await role_colour(message))
                if not matches:
                    embed.add_field(name=f"No results for '{search}'", value="Try searching for something else.")
                    await console(f"User: {message.author} used TODO search command (error = no matches))")
                    await message.channel.send(embed=embed)
                    return
                else:
                    await console(f"User: {message.author} used TODO search command (matches = {len(matches)}))")
                    for i, match in enumerate(matches):
                        embed.add_field(name=f"{i+1}.", value=DATA["todo"][match], inline=False)
                    await message.channel.send(embed=embed)

    async def exit(self, message):
        if is_admin(message.author):
            await console(f"Admin: {message.author.id} used exit command")
            await message.channel.send("Exiting...")
            save()
            sys.exit()

    async def save(self, message):
        if is_admin(message.author):
            await console(f"Admin: {message.author.id} used save command")
            save()
            await message.channel.send("Saved.")

    async def console(self, message, *args):
        if is_admin(message.author):
            if len(args) >= 1:
                if args[0].lower() == "clear":
                    DATA["general"]["console"] = 0
                    await console(f"Admin: {message.author.id} used console command (operation = clear)")
                    await message.channel.send("Console channel has been cleared.")
                    return
                try:
                    print(args[0])
                    DATA["general"]["console"] = int(args[0])
                except TypeError:
                    await console(f"Admin: {message.author.id} used console command (error = invalid ID)")
                    await message.channel.send("Please use a numerical ID to change console channel.")
                    return
                await console(f"Admin: {message.author.id} used console command (new_ID = {args[0]})")
                await message.channel.send(f"Console channel ID has been changed to {args[0]}")
            else:
                await console(f"Admin: {message.author.id} used console command (error = no arguments)")
                await message.channel.send(f"Please pass an argument to change console channel.")




HANDLER = CommandHandle()

if __name__ == "__main__":
    BOT = None
    CLIENT.run(TOKEN)
