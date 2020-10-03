import requests

from utility.config_handler import get_config_value

s = requests.Session()
category = "MediaWiki"

wiki_url = "https://wiki.ariadna.su/"
api_url = "https://wiki.ariadna.su/api.php"


def create_a_token(token_type=None):
    if token_type is None:
        token_params = {'action': "query", 'meta': "tokens", 'format': "json"}
    else:
        token_params = {'action': "query", 'meta': "tokens", 'type': token_type, 'format': "json"}

    token_request = s.get(url=api_url, params=token_params)
    token_data = token_request.json()

    if token_type is None:
        return token_data['query']['tokens']['csrftoken']
    else:
        token_type += "token"
        return token_data['query']['tokens'][token_type]


def proceed_request_and_return_as_data(params, output=True):
    creation_request = s.post(api_url, data=params)
    if output:
        return creation_request.json()
    else:
        pass


login_token = create_a_token("login")

params_login = {
    'action': "login",
    'lgname': get_config_value(category, "login"),
    'lgpassword': get_config_value(category, "password"),
    'lgtoken': login_token,
    'format': "json"
}

login_request = proceed_request_and_return_as_data(params_login, False)


def create_wiki_account(username, password):
    creation_token = create_a_token(token_type="createaccount")

    creation_params = {
        'action': "createaccount",
        'createtoken': creation_token,
        'username': username,
        'password': password,
        'retype': password,
        'createreturnurl': wiki_url,
        'format': "json"
    }

    creation_data = proceed_request_and_return_as_data(creation_params)

    if creation_data['createaccount']['status'] == "FAIL":
        return creation_data['createaccount']['message']
    else:
        return True


def ban_wiki_account(username, reason):
    ban_token = create_a_token()

    ban_params = {
        "action": "block",
        "user": username,
        "expiry": "Never",
        "reason": reason,
        "token": ban_token,
        "format": "json"
    }

    ban_data = proceed_request_and_return_as_data(ban_params)

    if list(ban_data.keys())[0] == "error":
        return ban_data['error']['info']
    else:
        return True


def unban_wiki_account(username, reason):
    unban_token = create_a_token()

    unban_params = {
        "action": "unblock",
        "user": username,
        "reason": reason,
        "token": unban_token,
        "format": "json"
    }

    unban_data = proceed_request_and_return_as_data(unban_params)

    if list(unban_data.keys())[0] == "error":
        return unban_data['error']['info']
    else:
        return True
