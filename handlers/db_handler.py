import bcrypt
import peewee as pw

from handlers.config_handler import get_config_value
from utility.password_util import hash_password_string

category = "MySQL"
db = pw.MySQLDatabase(get_config_value(category, "db"),
                      user=get_config_value(category, "username"),
                      password=get_config_value(category, "password"),
                      host=get_config_value(category, "address"),
                      port=int(get_config_value(category, "port")))


class BaseModel(pw.Model):
    class Meta:
        database = db


class Character(BaseModel):
    character = pw.CharField(max_length=15, unique=True)
    password = pw.CharField(max_length=60)
    discord_id = pw.CharField(max_length=18)
    wiki_link = pw.CharField(max_length=99)
    banned = pw.BooleanField(default=False)

    class Meta:
        table_name = 'character_database'


class Player(BaseModel):
    discord_id = pw.CharField(max_length=99)
    age_confirmation = pw.BooleanField(default=False)


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
    db.create_tables([Character, WikiUser, Player])


class AgeNotConfirmed(Exception):
    pass


@mysql_connection_decorator
def add_new_character(character, password, discord_id, wiki_link):
    if not get_if_age_confirmed(discord_id):
        raise AgeNotConfirmed
    else:
        password = hash_password_string(password)
        query = Character.create(character=character, password=password, discord_id=discord_id, wiki_link=wiki_link)
        return query


@mysql_connection_decorator
def get_if_age_confirmed(discord_id):
    query = Player.select().where((Player.discord_id == discord_id) & (Player.age_confirmation == 1)).count()
    if query == 0:
        raise AgeNotConfirmed()
    else:
        return True


@mysql_connection_decorator
def confirm_age(discord_id):
    query = Player.create(discord_id=discord_id, age_confirmation=True)
    return query


@mysql_connection_decorator
def remove_existing_character(character):
    query = Character.delete().where(Character.character == character).execute()
    return query


@mysql_connection_decorator
def remove_every_character(discord_id):
    query = Character.delete().where(Character.discord_id == discord_id).execute()
    return query


@mysql_connection_decorator
def get_all_characters_normal(discord_id):
    query = Character.select().where((Character.discord_id == discord_id) & (Character.banned == 0))
    return [player.character for player in query]


@mysql_connection_decorator
def get_all_characters_links(discord_id):
    query = Character.select().where(Character.discord_id == discord_id)
    return [player.wiki_link for player in query]


@mysql_connection_decorator
def get_character_link(character):
    query = Character.select().where(Character.character == character)
    for player in query:
        return player.wiki_link


@mysql_connection_decorator
def get_all_characters_raw(discord_id):
    query = Character.select().dicts().where(Character.discord_id == discord_id)
    return query


@mysql_connection_decorator
def set_new_password(character, password):
    query = Character.update(password=password).where(Character.character == character).execute()
    return query


# баны-бананы
@mysql_connection_decorator
def ban_player(discord_id):
    query = Character.update(banned=1).where(Character.discord_id == discord_id).execute()
    return query


@mysql_connection_decorator
def ban_character(character):
    query = Character.update(banned=1).where(Character.character == character).execute()
    return query


@mysql_connection_decorator
def unban_player(discord_id):
    query = Character.update(banned=0).where(Character.discord_id == discord_id).execute()
    return query


@mysql_connection_decorator
def unban_character(character):
    query = Character.update(banned=0).where(Character.character == character).execute()
    return query


@mysql_connection_decorator
def ban_player_status(discord_id):
    query = Character.select().where((Character.discord_id == discord_id) & (Character.banned == 1)).execute()
    return [player.character for player in query]


@mysql_connection_decorator
def ban_character_status(character):
    query = Character.select().where(Character.character == character).execute()
    for player in query:
        return player.banned


@mysql_connection_decorator
def ban_full_list():
    query = Character.select().where(Character.banned == 1).execute()
    return [player.character for player in query]


@mysql_connection_decorator
def is_such_char(character):
    query = Character.select().dicts().where((Character.character == character))
    if query.exists():
        return True
    else:
        return False


@mysql_connection_decorator
def check_user_password(character, password):
    password = str.encode(password)
    try:
        query = Character.get(Character.character == character).password
    except pw.DoesNotExist:
        return False
    if query:
        password_from_db = str.encode(query)
        if bcrypt.checkpw(password, password_from_db):
            return True
    else:
        return False
