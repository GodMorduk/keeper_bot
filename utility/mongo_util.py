import random

import discord

import constants
import handlers.mongo_handler as mng

stats_list_for_players = [
    "атрибут сила", "атрибут восприятие", "атрибут выносливость", "атрибут рефлексы", "атрибут ловкость",
    "атрибут удача", "навык психология", "навык управление", "навык воровство", "навык выживание", "навык работа",
    "навык биология", "навык инженерия", "навык колдовство", "навык исследование",
    "навык кузнечество", "навык магия"
]

stats_list_for_gms = [
    "поток красный", "поток синий", "поток индиго", "поток золотой", "поток серебряный", "усилие воздействие",
    "усилие знание", "усилие размышление", "усилие уверенность", "усилие репутация", "особое эститенция",
    "особое ордеция", "особое доп", "особое перки", "особое метки"
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
    "доп": "extra_perk_points",
    "перки": "taken_est_points",
    "метки": "mark"
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
    "удача": "lck"
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
    "колдовство": "sorcery",
    "кузнечество": "blacksmith",
    "магия": "magic"
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
    taken_by_perks = stats["special_stats"]["taken_est_points"]
    extra_perk_points = stats["special_stats"]["extra_perk_points"]
    marks = stats["special_stats"]["mark"]
    left_est = est - (mng.count_all_attrs(stats) + mng.count_all_skills(stats) + taken_by_perks)

    embed = discord.Embed()

    embed.colour = get_dominating_tide(stats["tides"])

    embed.title = stats["character"]

    if extra_perk_points > 0:
        embed.description = f'**Эститенции:** {est} + {extra_perk_points} (доп. очки)\n' \
                            f'**Занято перками:** {taken_by_perks}\n' \
                            f'**Свободно эститенции:** {left_est}\n' \
                            f'**Меток:** {marks}\n'
    else:
        embed.description = f'**Эститенции:** {est}\n' \
                            f'**Занято перками:** {taken_by_perks}\n' \
                            f'**Свободно эститенции:** {left_est}\n' \
                            f'**Меток:** {marks}\n'

    embed.add_field(name="Атрибуты:",
                    value=f'Сила: {stats["attributes"]["str"]}\n'
                          f'Восприятие: {stats["attributes"]["per"]}\n'
                          f'Выносливость: {stats["attributes"]["end"]}\n'
                          f'Рефлексы: {stats["attributes"]["ref"]}\n'
                          f'Ловкость: {stats["attributes"]["agi"]}\n'
                          f'Удача: {stats["attributes"]["lck"]}\n',
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
                    value=f'Психология: {stats["skills"]["psychology"]}\n'
                          f'Управление: {stats["skills"]["management"]}\n'
                          f'Воровство: {stats["skills"]["thievery"]}\n'
                          f'Выживание: {stats["skills"]["survival"]}\n'
                          f'Работа: {stats["skills"]["hardworking"]}\n'
                          f'Биология: {stats["skills"]["biology"]}\n',
                    inline=True)
    embed.add_field(name="\u200b",
                    value=f'Инженерия: {stats["skills"]["engineering"]}\n'
                          f'Колдовство: {stats["skills"]["sorcery"]}\n'
                          f'Исследование: {stats["skills"]["research"]}\n'
                          f'Кузнечество: {stats["skills"]["blacksmith"]}\n'
                          f'Магия: {stats["skills"]["magic"]}\n',
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


def beautify_citizen_info(citizen):
    embed = discord.Embed()
    embed.colour = discord.Colour.dark_red()
    if citizen is None:
        embed.title = "ОШИБКА!"
        embed.add_field(name="Код ошибки: 61252172", value="Информация по гражданину не найдена!")
    else:
        embed.title = "Гражданин номер " + citizen["discord_id"]
        embed.add_field(name="Социальный кредит:",
                        value=citizen["social_credit"],
                        inline=True)
        output = ""
        rewards = citizen["rewards"].items()
        for reward in rewards:
            if reward[1] != 0:
                output += reward[0] + ": " + str(reward[1]) + "\n"

        if output:
            embed.add_field(name="Награды:",
                            value=output,
                            inline=True)
    return embed
