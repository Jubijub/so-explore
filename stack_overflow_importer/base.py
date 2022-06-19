"""Common methods to handle Stack Exchange API"""

import requests


BASE_SITE = "https://api.stackexchange.com"
VERSION = "2.3"


def query_method(method: str, key: str, access_token: str, params: dict):
    """Queries a Stack Exchange API endpoint and provides the JSON response.

    Parameters
    ----------
        method: the method name, such as `questions` or `info`. Valid method names can
        be found at https://api.stackexchange.com/docs .

        key: the API key, provided by completing
        https://stackapps.com/apps/oauth/register registration

        access_tocken: the API access token provided by granting this app access,
        by calling `get_access_token_from_url()`

        params: a dict of parameters to pass to the API method. This method doesn't add
        any parameters, so the dict is expected to be complete (filters, etc...)
    """
    if not method:
        print("Please provide an method")
        return None

    if key:
        params["key"] = key

    if access_token:
        params["access_token"] = access_token

    if not params:
        print("Please provide a parameters dict")
        return None

    response = requests.get(f"{BASE_SITE}/{VERSION}/{method}", params=params)
    return response.json()
