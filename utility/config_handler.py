import configparser
import os
import sys

config = configparser.ConfigParser()
settings_path = "./settings.cfg"


def create_config(path):
    config.add_section("Discord")
    config.set("Discord", "token", "enter your token here")
    config.set("Discord", "registrar_role_id", "enter id here")
    config.set("Discord", "wiki-registrar_role_id", "enter id here")
    config.set("Discord", "log_channel_id", "enter id here")
    config.add_section("MySQL")
    config.set("MySQL", "Address", "localhost")
    config.set("MySQL", "Username", "db nickname")
    config.set("MySQL", "Password", "db password")
    config.set("MySQL", "DB", "db name")
    config.set("MySQL", "port", "3306")
    config.add_section("Client")
    config.set("Client", "dir_skins", "path to skins folder")
    config.set("Client", "dir_launcher", "path to launcher file")
    config.set("Client", "link_skins", "http link to skins website (and folder, if any)")
    config.set("Client", "launcher_name", "renamed launcher name")
    config.add_section("MediaWiki")
    config.set("MediaWiki", "login", "bot login")
    config.set("MediaWiki", "password", "bot password")
    config.set("MediaWiki", "change_password_script_path", "direct absolute path to file")
    config.set("MediaWiki", "rollback_script_path", "direct absolute path to file")

    with open(path, "w") as config_file:
        config.write(config_file)


def initialize_config():
    if not os.path.exists(settings_path):
        create_config(settings_path)
        print("Я не нашел конфиг и создал стандартный. Я закроюсь, заполните его как надо и запускайте еще раз.")
        sys.exit(0)
    else:
        print("Конфиг уже есть, пропускаю его создание.")


def get_config_value(category, value):
    config.read(settings_path)
    return config.get(category, value)
