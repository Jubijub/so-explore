""" Handling of Stack Exchange API authentification, and token management. """

import logging
import os
from colorama import Back, Fore, Style
from requests_oauthlib import OAuth2Session


so_logger = logging.getLogger("so_importer")


def retrieve_env_variable(variable_name: str | None) -> str | None:
    """Retrieves the key name `variable_name` from the environment variables

    Returns
    -------
        value: the environment variable value for the given name, or None if it couldn't
        be found.
    """
    if not variable_name:
        so_logger.error("An environment variable name must be supplied")
        return None
    if variable_name not in os.environ:
        so_logger.error("Couldn't find the environment variable %s.", variable_name)
        return None
    return os.environ[variable_name]


def retrieve_client_id() -> str | None:
    """Retrieves the API client ID from the environment variables (if it exists).

    Returns
    -------
        key : the API client ID from the variable SO_IMPORTER_CLIENT_ID
    """
    var = retrieve_env_variable("SO_IMPORTER_CLIENT_ID")
    if var:
        return var
    else:
        so_logger.error(
            "The Client ID is missing. Make sure to"
            " register your app to `https://stackapps.com/apps/oauth/register` and set"
            " the Environment variable `SO_IMPORTER_CLIENT_ID` with the `clientID`"
            " value provided by StackApps."
        )


def retrieve_key() -> str | None:
    """Retrieves the API key from the environment variables (if it exists).

    Returns
    -------
        key : the API key from the variable SO_IMPORTER_KEY
    """
    var = retrieve_env_variable("SO_IMPORTER_KEY")
    if var:
        return var
    else:
        so_logger.error(
            "The key is missing. Make sure to"
            " register your app to `https://stackapps.com/apps/oauth/register` and set"
            " the Environment variable `SO_IMPORTER_KEY` with the `key` value provided"
            " by StackApps."
        )


def retrieve_token() -> str | None:
    """Retrieves the API token from the environment variables (if it exists).

    Returns
    -------
        token : the API token from the variable SO_IMPORTER_TOKEN
    """
    var = retrieve_env_variable("SO_IMPORTER_TOKEN")
    if var:
        return var
    else:
        so_logger.error(
            "The OAuth token is missing. Make sure to"
            " use this app with the `-auth` parameter and complete the authentication. "
            " The command line will print the token. Make sure to set the Environment"
            " variable `SO_IMPORTER_TOKEN` with the token provided."
        )


def get_authorization_url(client_id: str | None) -> tuple[str, str]:
    """Retrieves and displays the authorization URL for a given Stack overflow client ID.

    This URL is to be accessed in a browser to grant access to this application.

    Params
    ------
        client_id : the client ID given by StackApps upon registration

    Returns
    -------
        authorization_url : the authorization URL to be accessed in a browser.
        state : the OAuth state
    """
    redirect_uri = "https://stackexchange.com/oauth/login_success"
    scope = "no_expiry"

    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    authorization_url, state = oauth.authorization_url(
        "https://stackexchange.com/oauth/dialog"
    )
    print(
        f"{Fore.YELLOW+ Back.LIGHTBLACK_EX}Copy this URL to your browswer and complete"
        f" the authentication: {Style.RESET_ALL}"
        f"\n{Fore.BLUE}{authorization_url}"
    )
    assert isinstance(authorization_url, str)
    assert isinstance(state, str)
    return authorization_url, state


def get_access_token_from_url():
    """Extracts the Stack overflow access token from a user provided URL string.

    The URL typically comes from the `https://stackexchange.com/oauth/login_success`
    address bar, on which the user is redirected after approving access to this app.

    Returns
    -------
        access_token : the access token string
    """
    url = input(
        f"{Fore.YELLOW+ Back.LIGHTBLACK_EX}Paste here the login success"
        f" URL{Style.RESET_ALL}\n"
    )
    token = extract_token_from_url(url)
    print(
        "The token is"
        f" {Fore.GREEN+ Back.LIGHTBLACK_EX}{token}{Style.RESET_ALL}."
        f" {Fore.RED+ Back.LIGHTBLACK_EX}\nMake sure to set it as the environment"
        " variable SO_IMPORTER_TOKEN"
    )


def extract_token_from_url(url: str) -> str:
    """Extracts the token ID from a Stack Exchange login success address bar URL."""
    if not url:
        so_logger.error("You must provide a URL to extract the token from it.")
        raise ValueError("You must provide a URL to extract the token from it.")
    if not "https://stackexchange.com/oauth/" in url:
        so_logger.error(
            "The URL provided (%s) doesn't appear to come from Stack Exchange.",
            url,
        )
        raise ValueError(
            f"The URL provided ({url}) doesn't appear to come from Stack Exchange."
        )
    start_pattern = "access_token="
    end_pattern = "&state="
    start = url.find(start_pattern) + len(start_pattern)
    end = url.find(end_pattern, start)
    token = url[start:end]
    return token
