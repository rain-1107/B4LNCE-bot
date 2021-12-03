import json
import sys
from assets.scripts import bot, handler

PATH = "assets/data/"
DATA_FILE = "custom_data.json"  # This will have to be changed to 'default_data.json'
CONFIG_FILE = "custom_config.json"  # This will have to be changed to 'default_config.json'


with open(PATH + CONFIG_FILE, "r") as config:
    TOKEN = json.load(config)["token"]

if TOKEN == "Add bot token here":
    print(f"Add token to '{CONFIG_FILE}'")
    sys.exit()

with open(PATH + DATA_FILE, "r") as data:
    DATA = json.load(data)

if __name__ == "__main__":
    HANDLER = handler.init(DATA)
    bot.run(HANDLER, DATA, TOKEN)
