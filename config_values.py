from handlers.config_handler import config, settings_path

config.read(settings_path)

token = config["Discord"]["token"]
prefix = config["Discord"]["prefix"]
registrar_role = config["Discord"].getint("registrar_role_id")
wiki_registrar_role = config["Discord"].getint("wiki-registrar_role_id")
admin_role = config["Discord"].getint("admin_role_id")
owner_id = config["Discord"].getint("owner_id")
player_role_id = config["Discord"].getint("player_role_id")
timeout = config["Discord"].getfloat("timeout_max_time")

db_address = config["MySQL"]["address"]
db_username = config["MySQL"]["username"]
db_password = config["MySQL"]["password"]
db_name = config["MySQL"]["db"]
db_port = config["MySQL"].getint("port")

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
