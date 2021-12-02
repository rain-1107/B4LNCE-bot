import discord
import json
import sys
import bot
import handler

PATH = "assets/"
DATA_FILE = "custom_data.json" # This will have to be changed to 'default_data.json'
CONFIG_FILE = "custom_config.json"# This will have to be changed to 'default_config.json'


with open(PATH + CONFIG_FILE, "r") as config:
    TOKEN = json.load(config)["token"]

if TOKEN == "Add bot token here":
    print("Add token to '{config}' ".format(config=CONFIG_FILE))
    sys.exit()

with open(PATH + DATA_FILE, "r") as data:
    DATA = json.load(data)

if __name__ == "__main__":
	HANDLER = handler.init()
	bot.run(HANDLER)
