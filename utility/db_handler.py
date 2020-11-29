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


with db:
    db.create_tables([Player, WikiUser])


def add_new_player(character, password, discord_id, wiki_link):
    db.connect(reuse_if_open=True)
    Player.create(character=character, password=password, discord_id=discord_id, wiki_link=wiki_link)
    db.close()


def remove_existing_character(character):
    db.connect(reuse_if_open=True)
    Player.delete().where(Player.character == character).execute()
    db.close()

def remove_every_character(discord_id):
    db.connect(reuse_if_open=True)
    Player.delete().where(Player.discord_id == discord_id).execute()
    db.close()


def get_all_characters_normal(discord_id):
    db.connect(reuse_if_open=True)
    query = Player.select().where(Player.discord_id == discord_id)
    db.close()
    return [player.character for player in query]


def get_all_characters_links(discord_id):
    db.connect(reuse_if_open=True)
    query = Player.select().where(Player.discord_id == discord_id)
    db.close()
    return [player.wiki_link for player in query]


def get_character_link(character):
    db.connect(reuse_if_open=True)
    query = Player.select().where(Player.character == character)
    db.close()
    for player in query:
        return player.wiki_link


def get_all_characters_raw(discord_id):
    db.connect(reuse_if_open=True)
    query = Player.select().dicts().where(Player.discord_id == discord_id)
    db.close()
    return query


def set_new_password(character, password):
    db.connect(reuse_if_open=True)
    Player.update(password=password).where(Player.character == character).execute()
    db.close()


# баны-бананы
def ban_player(discord_id):
    db.connect(reuse_if_open=True)
    Player.update(banned=1).where(Player.discord_id == discord_id).execute()
    db.close()


def ban_character(character):
    db.connect(reuse_if_open=True)
    Player.update(banned=1).where(Player.character == character).execute()
    db.close()


def unban_player(discord_id):
    db.connect(reuse_if_open=True)
    Player.update(banned=0).where(Player.discord_id == discord_id).execute()
    db.close()


def unban_character(character):
    db.connect(reuse_if_open=True)
    Player.update(banned=0).where(Player.character == character).execute()
    db.close()


def ban_player_status(discord_id):
    db.connect(reuse_if_open=True)
    query = Player.select().where((Player.discord_id == discord_id) & (Player.banned == 1)).execute()
    db.close()
    return [player.character for player in query]


def ban_character_status(character):
    db.connect(reuse_if_open=True)
    query = Player.select().where(Player.character == character).execute()
    db.close()
    for player in query:
        return player.banned


def ban_full_list():
    db.connect(reuse_if_open=True)
    query = Player.select().where(Player.banned == 1).execute()
    db.close()
    return [player.character for player in query]
