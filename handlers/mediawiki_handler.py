import subprocess
from shlex import quote as shlex_quote

import aiohttp

import config_values

s = aiohttp.ClientSession()
category = "MediaWiki"

wiki_url = config_values.wiki_url
api_url = wiki_url + "api.php"

rollback_path = config_values.rollback_script_path
change_password_path = config_values.change_password_script_path


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
        'lgname': config_values.wiki_login,
        'lgpassword': config_values.wiki_password,
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


async def change_password(username, password):
    result = subprocess.run(
        f"php {change_password_path} --user={shlex_quote(username)} --password={shlex_quote(password)}",
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return str(result.stdout).rstrip("\n")


async def rollback(username):
    result = subprocess.run(
        f'php {rollback_path} --user={shlex_quote(username)} --summary=f"Откат {config_values.bot_genitive_name}"',
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return str(result.stdout).rstrip("\n")
