# Percival Bot

Your ultimate solution if you are me.

## Dependency
* Python 3.7.7+
* discord.py 1.5.0
* peewee 3.13.3
* aiofiles 0.5.0
* aiohttp 3.6.2


## Что он уже умеет

Префикс по умолчанию - !. Все команды кириллические, чтобы наверняка ни с чем не пересекаться. 

### Игроки:

Команда для справки - !персиваль

* Вывести всех персонажей игрока, что есть в базе данных.
* Вывести вики-ссылку на персонажа. Работает с базой данных игроков, поэтому ник должен быть на латиннице.
* Вывести вики-ссылки всех персонажей игрока. Команда с кулдауном 15 секунд.

Следующие команды работают только в личных сообщениях:

* Выдать лаунчер.
* Поменять пароль своего персонажа.
* Залить новый скин для персонажа, есть возможность задать постфикс (это не обязательно). Автоматически называет его под имя персонажа и добавляет постфикс через символ "_" (если был задан).
* Вывести все скины, чтобыли залиты под определенного персонажа. 
* Получить ссылку на скин по его полному названию.
* Уничтожить скин по его полному названию.

### Гейм-мастерка:

Команда для справки - !гейммастерская

* Регистрировать пользователей для игры
* Удалять их
* Делать полный дамп по одному из них
* Банить их (в бд, не на вики или в игре)
* Разбанивать (там же)
* Выводить инфу о забаненных персонажах одного игрока
* Проверять отдельного персонажа на бан
* Менять пароли игрокам

### Вики-мастерка:

Команда для справки - !викимастерская

* Регистрировать на вики.
* Банить на вики. 
* Разбанивать на вики. 
* Менять пароль на вики.
* Откатывать все правки пользователя. Откатываются только последние правки.

# To-do
* Интерактивные команды, состоящие из нескольких постов.
* Перевести sql-запросы на async. Сейчас в этом нет потребности ввиду низкой нагрузки, но все же.
