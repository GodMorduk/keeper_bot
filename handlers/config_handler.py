import configparser
import os
import sys

config = configparser.ConfigParser()
settings_path = "./settings.cfg"


def create_config(path):
    config.add_section("Discord")
    config["Discord"]["token"] = "enter your token here"
    config["Discord"]["prefix"] = "enter your prefix, i.e \"!\""
    config["Discord"]["registrar_role_id"] = "enter id here"
    config["Discord"]["wiki-registrar_role_id"] = "enter id here"
    config["Discord"]["admin_role_id"] = "enter admin group id"
    config["Discord"]["owner_id"] = "enter owner id here"
    config["Discord"]["player_role_id"] = "enter player role id here"
    config["Discord"]["timeout_max_time"] = "enter interactive commands max timeout"
    config.add_section("MySQL")
    config["MySQL"]["address"] = "localhost"
    config["MySQL"]["username"] = "db username"
    config["MySQL"]["password"] = "db password"
    config["MySQL"]["db"] = "database name"
    config["MySQL"]["port"] = "3306"
    config.add_section("Game")
    config["Game"]["dir_skins"] = "path to skins folder"
    config["Game"]["dir_launcher"] = "path to launcher file"
    config["Game"]["link_skins"] = "http link to skins website (and folder]"
    config["Game"]["launcher_name"] = "renamed launcher name"
    config.add_section("MediaWiki")
    config["MediaWiki"]["url"] = "enter wiki url, like https://wiki.example.com/"
    config["MediaWiki"]["login"] = "bot login to Mediawiki"
    config["MediaWiki"]["password"] = "bot password to Mediawiki"
    config["MediaWiki"]["change_password_script_path"] = "direct absolute path to file"
    config["MediaWiki"]["rollback_script_path"] = "direct absolute path to file"
    config.add_section("Errors")
    config["Errors"]["log_enable"] = "enable error logging in channel provided below"
    config["Errors"]["log_channel_id"] = "enter id here"

    with open(path, "w") as config_file:
        config.write(config_file)


def initialize_config():
    if not os.path.exists(settings_path):
        create_config(settings_path)
        print("Я не нашел конфиг и создал стандартный. Я закроюсь, заполните его как надо и запускайте еще раз.")
        sys.exit(0)
    else:
        print("Этого вывода вообще не должно быть, но конфиг успешно загружен.")
