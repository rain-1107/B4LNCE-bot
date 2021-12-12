import random
import discord
import sys
import json

CLIENT: discord.Client


async def role_colour(message):
    roles = await message.guild.fetch_roles()
    highest = discord.utils.find(lambda role: role in roles,
                                 reversed(message.guild.get_member(CLIENT.user.id).roles))
    return highest.colour


async def console(str, client):
    print(str)
    if DATA["general"]["console"] != 0:
        guild = await client.fetch_guild(DATA["general"]["guild"])
        for channel in await guild.fetch_channels():
            if channel.id == int(DATA["general"]["console"]):
                await channel.send(str)
                return


def save(path):
    with open(path, "w") as data:
        json.dump(DATA, data, indent=2)


def is_admin(user: discord.User):
    for admin in DATA["general"]["admin_ids"]:
        if user.id == admin:
            return True
    return False


class CommandHandle:
    def __init__(self, save_path):
        self.commands = {"ping": self.ping, "echo": self.echo, "help": self.help, "todo": self.todo, "exit": self.exit, "save": self.save ,"console": self.console, "whitelist": self.whitelist}
        self.save_path = save_path

    def set_client(self, client):
        global CLIENT
        CLIENT = client

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
        await console(f"User: {message.author} used help command (admin = {admin})", CLIENT)
        await message.channel.send(embed=embed)

    async def ping(self, message):
        embed = discord.Embed(title="Pong", colour=await role_colour(message))
        ping = round(CLIENT.latency * 1000)
        if ping > 100:
            desc = "Running pretty slow"
        else:
            desc = "I am speed"
        embed.add_field(name=str(ping) + " ms", value=desc, inline=True)
        await console(f"User: {message.author} used ping command (ping = {ping})", CLIENT)
        await message.channel.send(embed=embed)

    async def echo(self, message, *echo):
        send = ""
        for word in echo:
            send += word+" "
        if send != "":
            await message.channel.send(send)
            await console(f"User: {message.author} used echo command (echo = {send})", CLIENT)
        else:
            await console(f"User: {message.author} used echo command (error = no arguments passed))", CLIENT)

    async def todo(self, message, *args):
        if len(args) == 0:
            embed = discord.Embed(title="TODO", colour=await role_colour(message))
            list = DATA["todo"]
            if len(list) == 0:
                embed.add_field(name="Nothing in the TODO list.", value=f"Add something with {DATA['general']['prefix']}todo add")
            else:
                for i, todo in enumerate(DATA["todo"]):
                    embed.add_field(name=f"{i+1}.", value=todo, inline=False)
            await console(f"User: {message.author} used TODO command (todo = {DATA['todo']}))", CLIENT)
            await message.channel.send(embed=embed)

        elif args[0].lower() == "add":
            add = ""
            for word in args[1:]:
                add += word+" "
            add = add[:len(add)-1]
            DATA["todo"].append(add)
            await console(f"User: {message.author} used TODO add command (added = {add}))", CLIENT)
            await message.channel.send(f"Added '{add}' to the TODO list.")

        elif args[0].lower() == "remove":
            try:
                index = int(args[1])-1
                try:
                    removed = DATA["todo"].pop(index)
                except IndexError:
                    await console(f"User: {message.author} used TODO remove command (error = point did not exist))", CLIENT)
                    await message.channel.send("That number point does not exist.")
                    return
                await console(f"User: {message.author} used TODO remove command (removed = {removed}))", CLIENT)
                await message.channel.send(f"Removed '{removed}' from the TODO list.")
            except TypeError:
                await console(f"User: {message.author} used TODO remove command (error = argument was not passed))", CLIENT)
                await message.channel.send("Use a number to signify which point to remove.")
            except IndexError:
                await console(f"User: {message.author} used TODO remove command (error = no argument passed))", CLIENT)
                await message.channel.send("Add a number to signify which point to remove.")

        elif args[0].lower() == "search":
            if len(args) == 1:
                await console(f"User: {message.author} used TODO search command (error = no arguments passed))", CLIENT)
                await message.channel.send("Please search for something.")
                return
            else:
                search = ""
                for word in args[1:]:
                    search += word + " "
                search = search[:len(search)-1]
                matches = []
                for i, point in enumerate(DATA["todo"]):
                    if search in point:
                        matches.append(i)
                s = ""
                if len(matches) != 1: s = "s"
                embed = discord.Embed(title=f"{len(matches)} Result{s}", colour=await role_colour(message))
                if not matches:
                    embed.add_field(name=f"No results for '{search}'", value="Try searching for something else.")
                    await console(f"User: {message.author} used TODO search command (error = no matches))", CLIENT)
                    await message.channel.send(embed=embed)
                    return
                else:
                    await console(f"User: {message.author} used TODO search command (matches = {len(matches)}))", CLIENT)
                    for i, match in enumerate(matches):
                        embed.add_field(name=f"{i+1}.", value=DATA["todo"][match], inline=False)
                    await message.channel.send(embed=embed)

        elif args[0].lower() == "pick":
            if len(args) == 1:
                pick = random.choice(DATA["todo"])
                await console(f"User: {message.author} used TODO pick command (pick = {pick}))", CLIENT)
                embed = discord.Embed(title=f"Random TODO Point", colour=await role_colour(message))
                embed.add_field(name=str(DATA['todo'].index(pick)+1)+".", value=pick)
                await message.channel.send(embed=embed)
            else:
                search = ""
                for word in args[1:]:
                    search += word + " "
                search = search[:len(search)-1]
                matches = []
                for i, point in enumerate(DATA["todo"]):
                    if search in point.lower():
                        matches.append(i)
                if not matches:
                    await console(f"User: {message.author} used TODO pick search command (error = no results))", CLIENT)
                    await message.channel.send(f"No results for '{search}'")
                    return
                pick = random.choice(matches)
                await console(f"User: {message.author} used TODO pick search command (search = {search}, pick = {pick}))", CLIENT)
                embed = discord.Embed(title=f"Random TODO Point", colour=await role_colour(message))
                embed.add_field(name=str(pick+1)+".", value=DATA['todo'][pick])
                await message.channel.send(embed=embed)

    async def exit(self, message):
        if is_admin(message.author):
            await console(f"Admin: {message.author.id} used exit command", CLIENT)
            await message.channel.send("Exiting...")
            save(self.save_path)
            sys.exit()

    async def save(self, message):
        if is_admin(message.author):
            await console(f"Admin: {message.author.id} used save command", CLIENT)
            save(self.save_path)
            await message.channel.send("Saved.")

    async def console(self, message, *args):
        if is_admin(message.author):
            if len(args) >= 1:
                if args[0].lower() == "clear":
                    DATA["general"]["console"] = 0
                    await console(f"Admin: {message.author.id} used console command (operation = clear)", CLIENT)
                    await message.channel.send("Console channel has been reset.")
                    return
                try:
                    print(args[0])
                    DATA["general"]["console"] = int(args[0])
                except TypeError:
                    await console(f"Admin: {message.author.id} used console command (error = invalid ID)", CLIENT)
                    await message.channel.send("Please use a numerical ID to change console channel.")
                    return
                await console(f"Admin: {message.author.id} used console command (new_ID = {args[0]})", CLIENT)
                await message.channel.send(f"Console channel ID has been changed to {args[0]}")
            else:
                await console(f"Admin: {message.author.id} used console command (error = no arguments)", CLIENT)
                await message.channel.send(f"Please pass an argument to change console channel.")

    async def whitelist(self, message, *args):
        if is_admin(message.author):
            if len(args) >=2:
                if args[0].lower() == "add":
                    try:
                        DATA["general"]["whitelist"].append(int(args[1]))
                    except TypeError:
                        await console(f"Admin: {message.author.id} used whitelist add command (error = invalid ID)", CLIENT)
                        await message.channel.send(f"Please pass a valid user ID.")
                    await console(f"Admin: {message.author.id} used whitelist add command (ID = {args[1]})", CLIENT)
                    await message.channel.send(f"Add '{args[1]} to whitelist'")
                    return
                elif args[0].lower() == "remove":
                    try:
                        DATA["general"]["whitelist"].pop(DATA["general"]["whitelist"].index(int(args[1])))
                    except IndexError:
                        await console(f"Admin: {message.author.id} used whitelist remove command (error = invalid ID)", CLIENT)
                        await message.channel.send(f"Please pass a valid user ID.")
                    await console(f"Admin: {message.author.id} used whitelist remove command (ID = {args[1]})", CLIENT)
                    await message.channel.send(f"Removed '{args[1]} to whitelist'")
                    return
            else:
                embed = discord.Embed(title=f"Whitelist", colour=await role_colour(message))
                for id in DATA["general"]["whitelist"]:
                    user = await CLIENT.fetch_user(id)
                    embed.add_field(name=user.name, value=str(id), inline=False)
                await message.channel.send(embed=embed)
                return


DATA = {}


def init(data, save_path):
    global DATA
    DATA = data
    return CommandHandle(save_path)