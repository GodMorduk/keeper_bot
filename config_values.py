from handlers.config_handler import config, settings_path

config.read(settings_path, encoding="utf-8")

token = config["Discord"]["token"]
prefix = config["Discord"]["prefix"]
registrar_role = config["Discord"].getint("registrar_role_id")
wiki_registrar_role = config["Discord"].getint("wiki-registrar_role_id")
gm_role = config["Discord"].getint("gm_role_id")
tech_gm_role = config["Discord"].getint("tech_gm_role_id")
admin_role = config["Discord"].getint("admin_role_id")
owner_id = config["Discord"].getint("owner_id")
player_role_id = config["Discord"].getint("player_role_id")
timeout = config["Discord"].getfloat("timeout_max_time")
age_confirmation_categories = config["Discord"]["age_confirmation_categories"].split(",")

db_address = config["Database"]["address"]

mysql_username = config["MySQL"]["username"]
mysql_password = config["MySQL"]["password"]
mysql_name = config["MySQL"]["name"]
mysql_port = config["MySQL"].getint("port")

mongodb_username = config["MongoDB"]["username"]
mongodb_password = config["MongoDB"]["password"]
mongodb_name = config["MongoDB"]["name"]
mongodb_port = config["MongoDB"].getint("port")

dir_skins = config["Game"]["dir_skins"]
dir_launcher = config["Game"]["dir_launcher"]
link_skins = config["Game"]["link_skins"]
launcher_name = config["Game"]["launcher_name"]

wiki_url = config["MediaWiki"]["url"]
wiki_login = config["MediaWiki"]["login"]
wiki_password = config["MediaWiki"]["password"]
change_password_script_path = config["MediaWiki"]["change_password_script_path"]
rollback_script_path = config["MediaWiki"]["rollback_script_path"]

log_enable = config["Errors"].getboolean("log_enable")
log_channel = config["Errors"].getint("log_channel_id")

bot_name = config["Extra"]["bot_name"]
bot_genitive_name = config["Extra"]["bot_genitive_name"]

server_address = config["Server"]["address"]
server_port = config["Server"].getint("port")
online_delete_after = config["Server"].getint("online_delete_after")
