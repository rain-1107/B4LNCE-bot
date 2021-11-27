import discord
import json
import sys

INTENTS = discord.Intents.default()
# INTENTS.members = True \\ This line breaks this script but is needed for whitelist check
CLIENT = discord.Client(intents=INTENTS)
JSON_PATH = "assets\\data.json"

try:
    with open("assets\\my_config.json", "r") as config:
        TOKEN = json.load(config)["token"]
except:
    with open("assets\\config.json", "r") as config:
        TOKEN = json.load(config)["token"]
    if TOKEN == "Add bot token here":
        print("Add token to 'config.json'")
        sys.exit()

with open(JSON_PATH, "r") as json_file:
    DATA = json.load(json_file)


async def role_colour(message):
    roles = await message.guild.fetch_roles()
    highest = discord.utils.find(lambda role: role in roles,
                                 reversed(message.guild.get_member(CLIENT.user.id).roles))
    return highest.colour


def save():
    with open(JSON_PATH, "w") as json_file:
        json.dump(DATA, json_file, indent=2)


def is_admin(user: discord.User):
    for admin in DATA["general"]["admin_ids"]:
        if user.id == admin:
            return True
    return False


@CLIENT.event
async def on_ready():
    global BOT
    BOT = CLIENT.user
    print(f"{BOT} is online.")
    await CLIENT.change_presence(activity=discord.Game(name="!help"))
    guilds = await CLIENT.fetch_guilds().flatten()
    if len(guilds) > 1:
        print(f"{BOT.name} is in more than one server, leaving servers not recognised")
        for guild in guilds:
            if guild.id != DATA["general"]["guild"]:
                print(f"{BOT.name} left server: {guild.id}")
                await guild.leave()
    guilds = await CLIENT.fetch_guilds().flatten()
    for guild in guilds:
        print(f"Confirming whitelist in server: {guild.name}")
        members = guild.members
        if members == []:
            print("Bot has not been set up correctly cannot confirm whitelist")
        for member in members:
            print(member.name)
            if member.id not in DATA["general"]["whitelist"]:
                print(f"{member.user} not whitelisted, kicking from server")
                try:
                    print(f"{member.user} was kicked from server")
                    await member.kick(reason="User not whitelisted")
                except:
                    print("error: could not kick user from server")


@CLIENT.event
async def on_member_join(member):
    print(f"User: {member.user} joined server")
    if member.id not in DATA["general"]["whitelist"]:
        print(f"{member.user} not whitelisted, kicking from server")
        try:
            print(f"{member.user} was kicked from server")
            await member.kick(reason="User is not whitelisted")
        except:
            print("error: could not kick user from server")



@CLIENT.event
async def on_guild_join(guild):
    print(f"{BOT.name} joined a server")
    if guild.id != DATA["general"]["guild"]:
        print(f"{guild.name} is not a recognised server, leaving server")
        await guild.leave()


@CLIENT.event
async def on_message(message):
    if message.author != CLIENT.user:
        if message.content[0] == DATA["general"]["prefix"]:
            command = message.content[1:].split(" ")
            args = []
            if len(command) >= 2:
                args = command[1:]
            await HANDLER.handle(command[0], message, *args)


class CommandHandle:
    def __init__(self):
        self.commands = {"ping": self.ping, "echo": self.echo, "help": self.help, "todo": self.todo, "exit": self.exit, "save": self.save}

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
        print(f"User: {message.author} used help command (admin = {admin})")
        await message.channel.send(embed=embed)

    async def ping(self, message):
        embed = discord.Embed(title="Pong", colour=await role_colour(message))
        ping = round(CLIENT.latency * 1000)
        if ping > 100:
            desc = "Running pretty slow"
        else:
            desc = "I am speed"
        embed.add_field(name=str(ping) + " ms", value=desc, inline=True)
        print(f"User: {message.author} used ping command (ping = {ping})")
        await message.channel.send(embed=embed)

    async def echo(self, message, *echo):
        send = ""
        for word in echo:
            send += word+" "
        if send != "":
            await message.channel.send(send)
            print(f"User: {message.author} used echo command (echo = {send})")
        else:
            print(f"User: {message.author} used echo command (error = no arguments passed))")

    async def todo(self, message, *args):
        if len(args) == 0:
            embed = discord.Embed(title="TODO", colour=await role_colour(message))
            list = DATA["todo"]
            if len(list) == 0:
                embed.add_field(name="Nothing in the TODO list.", value=f"Add something with {DATA['general']['prefix']}todo add")
            else:
                for i, todo in enumerate(DATA["todo"]):
                    embed.add_field(name=f"{i+1}.", value=todo, inline=False)
            print(f"User: {message.author} used TODO command (todo = {DATA['todo']}))")
            await message.channel.send(embed=embed)

        elif args[0].lower() == "add":
            add = ""
            for word in args[1:]:
                add += word+" "
            add = add[:len(add)-1]
            DATA["todo"].append(add)
            print(f"User: {message.author} used TODO add command (added = {add}))")
            await message.channel.send(f"Added '{add}' to the TODO list.")

        elif args[0].lower() == "remove":
            try:
                index = int(args[1])-1
                try:
                    removed = DATA["todo"].pop(index)
                except IndexError:
                    print(f"User: {message.author} used TODO remove command (error = point did not exist))")
                    await message.channel.send("That number point does not exist.")
                    return
                print(f"User: {message.author} used TODO remove command (removed = {removed}))")
                await message.channel.send(f"Removed '{removed}' from the TODO list.")
            except TypeError:
                print(f"User: {message.author} used TODO remove command (error = argument was not passed))")
                await message.channel.send("Use a number to signify which point to remove.")
            except IndexError:
                print(f"User: {message.author} used TODO remove command (error = no argument passed))")
                await message.channel.send("Add a number to signify which point to remove.")

        elif args[0].lower() == "search":
            if len(args) == 1:
                print(f"User: {message.author} used TODO search command (error = no arguments passed))")
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
                    print(f"User: {message.author} used TODO search command (error = no matches))")
                    await message.channel.send(embed=embed)
                    return
                else:
                    print(f"User: {message.author} used TODO search command (matches = {len(matches)}))")
                    for i, match in enumerate(matches):
                        embed.add_field(name=f"{i+1}.", value=DATA["todo"][match], inline=False)
                    await message.channel.send(embed=embed)

    async def exit(self, message):
        if is_admin(message.author):
            print(f"Admin: {message.author.id} used exit command")
            await message.channel.send("Exiting...")
            save()
            sys.exit()

    async def save(self, message):
        if is_admin(message.author):
            print(f"Admin: {message.author.id} used save command")
            save()
            await message.channel.send("Saved.")


HANDLER = CommandHandle()

if __name__ == "__main__":
    BOT = None
    CLIENT.run(TOKEN)
    
