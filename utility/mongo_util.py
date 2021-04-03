import random

import discord

import constants
import handlers.mongo_handler as mng

stats_list_for_players = [
    "атрибут сила", "атрибут восприятие", "атрибут выносливость", "атрибут рефлексы", "атрибут ловкость",
    "атрибут удача", "навык психология", "навык управление", "навык воровство", "навык выживание", "навык работа",
    "навык биология", "навык инженерия", "навык магия", "навык исследование", "навык оружейничество",
    "навык кузнечество", "навык магичность"
]

stats_list_for_gms = [
    "поток красный", "поток синий", "поток индиго", "поток золотой", "поток серебряный", "усилие воздействие",
    "усилие знание", "усилие размышление", "усилие уверенность", "усилие репутация", "особое эститенция",
    "особое ордеция", "особое перки"
]

dict_category = {
    "навык": "skills",
    "атрибут": "attributes",
    "усилие": "efforts",
    "поток": "tides",
    "особое": "special_stats"
}

dict_special = {
    "эститенция": "est",
    "ордеция": "ord",
    "перки": "extra_perk_points"
}

dict_tides = {
    "красный": "red",
    "синий": "blue",
    "индиго": "indigo",
    "золотой": "gold",
    "серебряный": "silver"
}

dict_attrs = {
    "сила": "str",
    "восприятие": "per",
    "выносливость": "end",
    "рефлексы": "ref",
    "ловкость": "agi",
    "удача": "luck"
}

dict_skills = {
    "психология": "psychology",
    "управление": "management",
    "воровство": "thievery",
    "выживание": "survival",
    "работа": "hardworking",
    "биология": "biology",
    "инженерия": "engineering",
    "исследование": "research",
    "магия": "magic",
    "кузнечество": "blacksmith",
    "магичность": "magical"
}

dict_efforts = {
    "воздействие": "impact",
    "знание": "knowledge",
    "размышление": "reflection",
    "уверенность": "confidence",
    "репутация": "reputation"
}


def get_dominating_tide(tides_dict):
    results = [key for (key, value) in tides_dict.items() if value == max(tides_dict.values())]
    if len(results) > 1:
        return constants.color_tides[random.choice([result for result in results])]
    else:
        return constants.color_tides[results[0]]


def beautify_char_stats(stats):
    est = stats["special_stats"]["est"]
    left_est = est - (mng.count_all_attrs(stats) + mng.count_all_skills(stats))

    embed = discord.Embed()

    embed.colour = get_dominating_tide(stats["tides"])

    embed.title = stats["character"]
    embed.description = f'**Эститенции:** {est} ' \
                        f'**Свободно эститенции:** {left_est}\n'

    embed.add_field(name="Атрибуты:",
                    value=f'Сила: {stats["attributes"]["STR"]}\n'
                          f'Восприятие: {stats["attributes"]["PER"]}\n'
                          f'Выносливость: {stats["attributes"]["END"]}\n'
                          f'Рефлексы: {stats["attributes"]["REF"]}\n'
                          f'Ловкость: {stats["attributes"]["AGI"]}\n'
                          f'Удача: {stats["attributes"]["LUCK"]}\n',
                    inline=True)
    embed.add_field(name="Потоки:",
                    value=f'Красный: {stats["tides"]["red"]}\n'
                          f'Синий: {stats["tides"]["blue"]}\n'
                          f'Индиго: {stats["tides"]["indigo"]}\n'
                          f'Золото: {stats["tides"]["gold"]}\n'
                          f'Серебряный: {stats["tides"]["silver"]}\n',
                    inline=True)
    embed.add_field(name="Усилия:",
                    value=f'Воздействия: {stats["efforts"]["impact"]}\n'
                          f'Знания: {stats["efforts"]["knowledge"]}\n'
                          f'Размышление: {stats["efforts"]["reflection"]}\n'
                          f'Уверенность: {stats["efforts"]["confidence"]}\n'
                          f'Репутация: {stats["efforts"]["reputation"]}\n',
                    inline=True)
    embed.add_field(name="Навыки:",
                    value=f'Психология: {stats["skills"]["Psychology"]}\n'
                          f'Управление: {stats["skills"]["Management"]}\n'
                          f'Воровство: {stats["skills"]["Thievery"]}\n'
                          f'Выживание: {stats["skills"]["Survival"]}\n'
                          f'Работа: {stats["skills"]["Hardworking"]}\n'
                          f'Биология: {stats["skills"]["Biology"]}\n',
                    inline=True)
    embed.add_field(name="\u200b",
                    value=f'Инженерия: {stats["skills"]["Engineering"]}\n'
                          f'Магия: {stats["skills"]["Magic"]}\n'
                          f'Исследование: {stats["skills"]["Research"]}\n'
                          f'Кузнечество: {stats["skills"]["Blacksmith"]}\n'
                          f'Магичность: {stats["skills"]["Magical"]}\n',
                    inline=True)
    return embed


def beautify_output_stats_names():
    embed = discord.Embed()
    embed.colour = discord.Colour.random()
    output = ""
    for stat in stats_list_for_players:
        output += stat + "\n"
    embed.add_field(name="Изменяемые игроками:",
                    value=output,
                    inline=True)
    output = ""
    for stat in stats_list_for_gms:
        output += stat + "\n"
    embed.add_field(name="Изменяемые ГМами:",
                    value=output,
                    inline=True)
    return embed
