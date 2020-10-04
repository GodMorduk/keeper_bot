import aiohttp
from aiohttp import web

from utility.config_handler import get_config_value

s = aiohttp.ClientSession()
category = "MediaWiki"

wiki_url = "https://wiki.ariadna.su/"
api_url = "https://wiki.ariadna.su/api.php"


async def create_a_token(token_type=None):
    if token_type is None:
        token_params = {'action': "query", 'meta': "tokens", 'format': "json"}
    else:
        token_params = {'action': "query", 'meta': "tokens", 'type': token_type, 'format': "json"}

    token_request = await s.get(url=api_url, params=token_params)
    token_data = await token_request.json()

    if token_type is None:
        return token_data['query']['tokens']['csrftoken']
    else:
        token_type += "token"
        return token_data['query']['tokens'][token_type]


async def proceed_request_and_return_as_data(params, output=True):
    creation_request = await s.post(api_url, data=params)
    fixed = await creation_request.json()
    if output:
        return fixed
    else:
        pass


async def mediawiki_login():
    login_token = await create_a_token("login")
    params_login = {
        'action': "login",
        'lgname': get_config_value(category, "login"),
        'lgpassword': get_config_value(category, "password"),
        'lgtoken': login_token,
        'format': "json"
    }
    await proceed_request_and_return_as_data(params_login, False)


async def create_wiki_account(username, password):
    creation_token = await create_a_token(token_type="createaccount")

    creation_params = {
        'action': "createaccount",
        'createtoken': creation_token,
        'username': username,
        'password': password,
        'retype': password,
        'createreturnurl': wiki_url,
        'format': "json"
    }

    creation_data = await proceed_request_and_return_as_data(creation_params)

    if creation_data['createaccount']['status'] == "FAIL":
        return creation_data['createaccount']['message']
    else:
        return True


async def ban_wiki_account(username, reason):
    ban_token = await create_a_token()

    ban_params = {
        "action": "block",
        "user": username,
        "expiry": "never",
        "reason": reason,
        "token": ban_token,
        "format": "json"
    }

    ban_data = await proceed_request_and_return_as_data(ban_params)

    if list(ban_data.keys())[0] == "error":
        return ban_data['error']['info']
    else:
        return True


async def unban_wiki_account(username, reason):
    unban_token = await create_a_token()

    unban_params = {
        "action": "unblock",
        "user": username,
        "reason": reason,
        "token": unban_token,
        "format": "json"
    }

    unban_data = await proceed_request_and_return_as_data(unban_params)

    if list(unban_data.keys())[0] == "error":
        return unban_data['error']['info']
    else:
        return True
