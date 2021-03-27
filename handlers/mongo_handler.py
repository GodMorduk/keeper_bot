import pymongo

import config_values

db = pymongo.MongoClient(config_values.db_address,
                         username=config_values.mongodb_username,
                         password=config_values.mongodb_password,
                         authSource=config_values.mongodb_name,
                         authMechanism='SCRAM-SHA-256',
                         port=config_values.mongodb_port)

col = db.characters.characters


class NotAStat(Exception):
    pass


class NotEnoughEst(Exception):
    pass


class InappropriateValue(Exception):
    pass


class NotAllowedStatLowering(Exception):
    pass


class StatLimit(Exception):
    pass


def exception_mongo_handler_decorator(func):
    async def exception_mongo_handler_wrapper(self, ctx, *args, **kwargs):
        try:
            func_execution = await func(self, ctx, args, kwargs)
        except NotAStat:
            await ctx.send("Ты хочешь поменять что-то, что не является навыком или атрибутом. Так нельзя. Отмена.")
            return
        except NotEnoughEst:
            await ctx.send("У тебя не хватит эститенции на это все. Отмена.")
            return
        except NotAllowedStatLowering:
            await ctx.send("Статы нельзя понижать. Обратись к ГМам.")
            return
        except StatLimit:
            await ctx.send("Это значение не может быть либо таким большим, либо меньше 0. Отмена.")
            return
        else:
            return func_execution

    return exception_mongo_handler_wrapper


def add(data, multiple=False):
    if multiple:
        col.insert(data)
    else:
        col.insert_one(data)


def get(data, multiple=False):
    if multiple:
        results = col.find(data)
        return results
    else:
        return col.find_one(data)


def delete(data, multiple=False):
    if multiple:
        col.delete(data)
    else:
        col.delete_one(data)


def update(entry_id, new_values):
    col.update_one({'_id': entry_id}, {'$set': new_values})


def update_char(char_entry):
    col.update_one({"_id": char_entry["_id"]}, {"$set": char_entry})


def create_new_character(name, discord_id, est=60):
    new_char_dict = {
        "character": name,
        "discord_user": f"{discord_id}",
        "re-specs": 1,
        "special_stats": {
            "est": est,
            "ord": 0,
            "extra_attr_points": 0,
            "extra_perk_points": 0
        },
        "tides": {
            "red": 0, "blue": 0, "indigo": 0, "gold": 0, "silver": 0
        },
        "attributes": {
            "STR": 0, "PER": 0, "END": 0, "REF": 0, "AGI": 0, "LUCK": 0
        },
        "skills": {
            "Psychology": 0, "Management": 0, "Thievery": 0, "Survival": 0, "Hardworking": 0, "Biology": 0,
            "Engineering": 0, "Magic": 0, "Research": 0, "Blacksmith": 0, "Magical": 0
        },
        "efforts": {
            "impact": 0, "knowledge": 0, "reflection": 0, "confidence": 0, "reputation": 0
        }
    }
    add(new_char_dict)


def count_all_skills(entry):
    all_skills = entry["skills"].values()
    est_cost = 0
    for skill in all_skills:
        if skill == 1:
            est_cost += 3
        elif skill == 2:
            est_cost += 7
        elif skill == 3:
            est_cost += 12
    return est_cost


def count_all_attrs(entry):
    return sum(entry["attributes"].values())


def change_stat(mongo_entry, category, name, modifier):
    est = mongo_entry["special_stats"]["est"]
    ext_ext = mongo_entry["special_stats"]["extra_attr_points"] + mongo_entry["special_stats"]["extra_perk_points"]

    if modifier.startswith("-"):
        raise NotAllowedStatLowering

    is_increment = modifier.startswith("+")

    modifier = int(modifier)

    curr_value = mongo_entry[category][name]
    if not is_increment and curr_value > modifier:
        raise NotAllowedStatLowering

    if is_increment is True:
        action = "$inc"
    else:
        action = "$set"

    if category == "attributes":
        if is_increment:
            mongo_entry[category][name] += modifier
            if curr_value + modifier >= 25:
                raise StatLimit
        else:
            mongo_entry[category][name] = modifier
            if modifier > 25:
                raise StatLimit
    elif category == "skills":
        if is_increment:
            mongo_entry[category][name] += modifier
            if curr_value + modifier >= 3:
                raise StatLimit
        else:
            mongo_entry[category][name] = modifier
            if modifier > 3:
                raise StatLimit
    elif category == "efforts":
        pass
    else:
        raise NotAStat

    if (est + ext_ext) - (count_all_skills(mongo_entry) + count_all_attrs(mongo_entry)) < 0:
        raise NotEnoughEst

    string = category + "." + name
    col.update_one({"_id": mongo_entry["_id"]}, {f"{action}": {f"{string}": modifier}})
    return get({"_id": mongo_entry["_id"]})[category][name]


def change_stat_gm(mongo_entry, category, name, modifier):
    is_increment = modifier.startswith(("+", "-"))

    if is_increment is True:
        action = "$inc"
    else:
        action = "$set"

    modifier = int(modifier)

    curr_value = mongo_entry[category][name]

    if category == "attributes":
        if is_increment:
            mongo_entry[category][name] += modifier
            if curr_value + modifier < 0 or curr_value + modifier > 25:
                raise StatLimit
        else:
            mongo_entry[category][name] = modifier
            if modifier < 0 or modifier > 25:
                raise StatLimit
    elif category == "skills":
        if is_increment:
            mongo_entry[category][name] += modifier
            if curr_value + modifier < 0 or curr_value + modifier > 3:
                raise StatLimit
        else:
            mongo_entry[category][name] = modifier
            if modifier < 0 or modifier > 3:
                raise StatLimit

    string = category + "." + name
    col.update_one({"_id": mongo_entry["_id"]}, {f"{action}": {f"{string}": int(modifier)}})
    return get({"_id": mongo_entry["_id"]})[category][name]
