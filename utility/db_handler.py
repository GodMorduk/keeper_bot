import peewee as pw

from utility.config_handler import get_config_value

category = "MySQL"
db = pw.MySQLDatabase(get_config_value(category, "db"),
                      user=get_config_value(category, "username"),
                      password=get_config_value(category, "password"),
                      host=get_config_value(category, "address"),
                      port=int(get_config_value(category, "port")))


class BaseModel(pw.Model):
    class Meta:
        database = db


class Player(BaseModel):
    character = pw.CharField(max_length=15)
    password = pw.CharField(max_length=15)
    discord_id = pw.CharField(max_length=18)
    wiki_link = pw.CharField(max_length=99)
    banned = pw.BooleanField(default=False)

    class Meta:
        table_name = 'character_database'


# заготовка на будущее, пока просто пустая бд
class WikiUser(BaseModel):
    wiki_account = pw.CharField(max_length=50)
    discord_id = pw.CharField(max_length=99)

    class Meta:
        table_name = 'wiki_users'


db.create_tables([Player, WikiUser])


def add_new_player(character, password, discord_id, wiki_link):
    Player.create(character=character, password=password, discord_id=discord_id, wiki_link=wiki_link)


def remove_existing_character(character):
    Player.delete().where(Player.character == character).execute()


def remove_every_character(discord_id):
    Player.delete().where(Player.discord_id == discord_id).execute()


def get_all_characters_normal(discord_id):
    query = Player.select().where(Player.discord_id == discord_id)
    return [player.character for player in query]


def get_all_characters_links(discord_id):
    query = Player.select().where(Player.discord_id == discord_id)
    return [player.wiki_link for player in query]


def get_character_link(character):
    query = Player.select().where(Player.character == character)
    for player in query:
        return player.wiki_link


def get_all_characters_raw(discord_id):
    query = Player.select().dicts().where(Player.discord_id == discord_id)
    return query


def set_new_password(character, password):
    Player.update(password=password).where(Player.character == character).execute()


# баны-бананы
def ban_player(discord_id):
    Player.update(banned=1).where(Player.discord_id == discord_id).execute()


def ban_character(character):
    Player.update(banned=1).where(Player.character == character).execute()


def unban_player(discord_id):
    Player.update(banned=0).where(Player.discord_id == discord_id).execute()


def unban_character(character):
    Player.update(banned=0).where(Player.character == character).execute()


def ban_player_status(discord_id):
    query = Player.select().where((Player.discord_id == discord_id) & (Player.banned == 1)).execute()
    return [player.character for player in query]


def ban_character_status(character):
    query = Player.select().where(Player.character == character).execute()
    for player in query:
        return player.banned


def ban_full_list():
    query = Player.select().where(Player.banned == 1).execute()
    return [player.character for player in query]
