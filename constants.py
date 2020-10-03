from utility.config_handler import get_config_value

discord_category = "Discord"
token = get_config_value(discord_category, "token")
registrar_role = int(get_config_value(discord_category, "registrar_role_id"))
log_channel = int(get_config_value(discord_category, "log_channel_id"))
wiki_registrar_role = int(get_config_value(discord_category, "registrar_role_id"))

client_category = "Client"
dir_skins = get_config_value(client_category, "dir_skins")
dir_launcher = get_config_value(client_category, "dir_launcher")
link_skins = get_config_value(client_category, "link_skins")

color_codes = {"Error": 15158332, "Log": 3066993, "Info": 14793122}