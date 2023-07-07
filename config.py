import configparser
import os
import time

path = 'config.cfg'

def create_config():

    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "bot_token", "0")
    config.set("Settings", "bot_login", "0")
    config.set("Settings", "admin_id", "0:")
    config.set("Settings", "channel_id", "0")
    config.set("Settings", "admin_group", "0")
    config.set("Settings", "qiwi_number", "0")
    config.set("Settings", "qiwi_token", "0")
    config.set("Settings", "secret_key", "0")
    config.set("Settings", "percent", "0")
    config.set("Settings", "min_bank", "0")
    config.set("Settings", "min_withdraw_sum", "0")
    config.set("Settings", "commission_percent", "0")
    config.set("Settings", "ref_reward", "0")
    config.set("Settings", "ref_percent", "0") 
    config.set("Settings", "range_game_list", "0")
    config.set("Settings", "admin_link", "0")
    config.set("Settings", "coder_link", "0")
    config.set("Settings", "channel_link", "0")
    config.set("Settings", "group_link", "0")
    
    with open(path, "w") as config_file:
        config.write(config_file)

def check_config_file():
    if not os.path.exists(path):
        create_config()
        
        print('Config created')
        time.sleep(3)
        exit(0)


def config(what):
    
    config = configparser.ConfigParser()
    config.read(path)

    value = config.get("Settings", what)

    return value

def edit_config(setting, value):
    config = configparser.ConfigParser()
    config.read(path)

    config.set("Settings", setting, value)

    with open(path, "w") as config_file:
        config.write(config_file)

check_config_file()