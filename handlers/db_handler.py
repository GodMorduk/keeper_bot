import peewee as pw

from handlers.config_handler import get_config_value

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
    character = pw.CharField(max_length=15, unique=True)
    password = pw.CharField(max_length=15)
    discord_id = pw.CharField(max_length=18)
    wiki_link = pw.CharField(max_length=99)
    banned = pw.BooleanField(default=False)

    class Meta:
        table_name = 'character_database'


# заготовка на будущее, пока просто пустая бд
class WikiUser(BaseModel):
    wiki_account = pw.CharField(max_length=50, unique=True)
    discord_id = pw.CharField(max_length=99)

    class Meta:
        table_name = 'wiki_users'


def mysql_connection_decorator(func):
    def ensure_mysql_connect(*args, **kwargs):
        db.connect(reuse_if_open=True)
        func_execution = func(*args, **kwargs)
        db.close()
        return func_execution

    return ensure_mysql_connect


with db:
    db.create_tables([Player, WikiUser])


@mysql_connection_decorator
def add_new_player(character, password, discord_id, wiki_link):
    query = Player.create(character=character, password=password, discord_id=discord_id, wiki_link=wiki_link)
    return query


@mysql_connection_decorator
def remove_existing_character(character):
    query = Player.delete().where(Player.character == character).execute()
    return query


@mysql_connection_decorator
def remove_every_character(discord_id):
    query = Player.delete().where(Player.discord_id == discord_id).execute()
    return query


@mysql_connection_decorator
def get_all_characters_normal(discord_id):
    query = Player.select().where((Player.discord_id == discord_id) & (Player.banned == 0))
    return [player.character for player in query]


@mysql_connection_decorator
def get_all_characters_links(discord_id):
    query = Player.select().where(Player.discord_id == discord_id)
    return [player.wiki_link for player in query]


@mysql_connection_decorator
def get_character_link(character):
    query = Player.select().where(Player.character == character)
    for player in query:
        return player.wiki_link


@mysql_connection_decorator
def get_all_characters_raw(discord_id):
    query = Player.select().dicts().where(Player.discord_id == discord_id)
    return query


@mysql_connection_decorator
def set_new_password(character, password):
    query = Player.update(password=password).where(Player.character == character).execute()
    return query


# баны-бананы
@mysql_connection_decorator
def ban_player(discord_id):
    query = Player.update(banned=1).where(Player.discord_id == discord_id).execute()
    return query


@mysql_connection_decorator
def ban_character(character):
    query = Player.update(banned=1).where(Player.character == character).execute()
    return query


@mysql_connection_decorator
def unban_player(discord_id):
    query = Player.update(banned=0).where(Player.discord_id == discord_id).execute()
    return query


@mysql_connection_decorator
def unban_character(character):
    query = Player.update(banned=0).where(Player.character == character).execute()
    return query


@mysql_connection_decorator
def ban_player_status(discord_id):
    query = Player.select().where((Player.discord_id == discord_id) & (Player.banned == 1)).execute()
    return [player.character for player in query]


@mysql_connection_decorator
def ban_character_status(character):
    query = Player.select().where(Player.character == character).execute()
    for player in query:
        return player.banned


@mysql_connection_decorator
def ban_full_list():
    query = Player.select().where(Player.banned == 1).execute()
    return [player.character for player in query]


@mysql_connection_decorator
def is_such_char(character):
    query = Player.select().dicts().where((Player.character == character))
    if query.exists():
        return True
    else:
        return False
