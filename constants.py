from utility.config_handler import get_config_boolean_value
from utility.config_handler import get_config_value

discord_category = "Discord"
token = get_config_value(discord_category, "token")
registrar_role = int(get_config_value(discord_category, "registrar_role_id"))
wiki_registrar_role = int(get_config_value(discord_category, "registrar_role_id"))
admin_role = int(get_config_value(discord_category, "admin_role_id"))
owner_id = int(get_config_value(discord_category, "owner_id"))

client_category = "Client"
dir_skins = get_config_value(client_category, "dir_skins")
dir_launcher = get_config_value(client_category, "dir_launcher")
link_skins = get_config_value(client_category, "link_skins")
launcher_name = get_config_value(client_category, "launcher_name")

log_category = "Logging"
log_enable = get_config_boolean_value(log_category, "log_enable")
log_channel = int(get_config_value(log_category, "log_channel_id"))

color_codes = {"Error": 15158332, "Log": 3066993, "Info": 14793122}
