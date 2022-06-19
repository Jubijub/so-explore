"""Script to auto update the question bank from Stack Exchange."""
from argparse import Namespace
import argparse
import logging
import colorama
import coloredlogs

from stack_overflow_importer.auth import (
    get_access_token_from_url,
    get_authorization_url,
    retrieve_client_id,
    retrieve_key,
    retrieve_token,
)


def init_logging() -> logging.Logger:
    """Initializes console and file logging.

    Returns
    -------
        a logger with a console and file handler
    """
    logger = logging.getLogger("so_importer")
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler("./so_importer.log")
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    coloredlogs.install(
        level="INFO",
        logger=logger,
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.info("****** Program start ******")
    return logger


so_logger = init_logging()


def print_check_result(client_id, key, token):
    """Displays the detailed check results to confirm all Env variables are properly
    set."""
    if not client_id:
        so_logger.error(
            "The client_ID is missing. Make sure to"
            " register your app to `https://stackapps.com/apps/oauth/register` and set"
            " the Environment variable `SO_IMPORTER_CLIENT_ID` with the `clientID`"
            " value provided by StackApps."
        )
    if not key:
        so_logger.error(
            "The key is missing. Make sure to"
            " register your app to `https://stackapps.com/apps/oauth/register` and set"
            " the Environment variable `SO_IMPORTER_KEY` with the `key` value provided"
            " by StackApps."
        )
    if not token:
        so_logger.error(
            "The OAuth token is missing. Make sure to"
            " use this app with the `-auth` parameter and complete the authentication. "
            " The command line will print the token. Make sure to set the Environment"
            " variable `SO_IMPORTER_TOKEN` with the token provided."
        )
    so_logger.info("All environment variables could be retrieved.")


def parse_args(args: list[str]) -> Namespace:
    """Parses the command line arguments and trigger the relevant actions.

    Arguments
    ----------
        args: a List of string arguments such as sys.argv

    Returns
    -------
        a Namespace object containing the parsed arguments
    """
    parser = argparse.ArgumentParser(
        args,
        description="Utility to import Stack overflow questions.",
    )
    subparsers = parser.add_subparsers(
        dest="action",
        help="desired action for this program.",
        required=True,
    )
    # pylint: disable=unused-variable
    parser_check = subparsers.add_parser(
        "check",
        help="checks that the StackExchange API keys and tokens are set properly.",
    )
    # pylint: disable=unused-variable
    parser_auth = subparsers.add_parser(
        "auth",
        help="triggers the API authentication process to obtain an API token.",
    )

    parser_fetch = subparsers.add_parser(
        "fetch",
        help="retrieves Stack Overflow topics and update the result database.",
    )
    parser_fetch.add_argument(
        "--filter",
        help="The hash of a filter, as provided by filters/create API method.",
    )
    parser_fetch.add_argument(
        "--page",
        help=(
            "If results fit more than one page, which page to return. 1 is the first"
            " page."
        ),
        type=int,
    )
    parser_fetch.add_argument(
        "--pagesize",
        help="Defines how many results to provide per page, between 0 and 100.",
        type=int,
    )
    parser_fetch.add_argument(
        "--fromdate",
        help=(
            "Retrieve all questions from this date. If not supplied, will retrieve all"
            " questions."
        ),
    )
    parser_fetch.add_argument(
        "--todate",
        help=(
            "Retrieve all questions until this date. If not supplied, will retrieve all"
            " questions until now."
        ),
    )
    parser_fetch.add_argument(
        "--order",
        help="The order in which to sort the results.",
    )
    parser_fetch.add_argument(
        "--min",
        help="For sort by activity/creation/votes, defines the minimum value to return",
    )
    parser_fetch.add_argument(
        "--max",
        help="For sort by activity/creation/votes, defines the maximum value to return",
    )
    parser_fetch.add_argument(
        "--sort",
        help=(
            "Which sorting method to use : activity, creation, votes, hot, week, month"
        ),
    )
    parser_fetch.add_argument(
        "--tagged",
        help=(
            "Semi-colon delimited list of tags. Will return questions which match all"
            " tags."
        ),
    )
    return parser.parse_args(args)

    # filter: str = None,
    # page: int = None,
    # pagesize: int = None,
    # fromdate: int = None,
    # todate: int = None,
    # order: Order = None,
    # # pylint: disable=redefined-builtin
    # min: int = None,
    # max: int = None,
    # sort: QuestionSortMethod = None,
    # tagged: str = None,


def main():
    """Main logic."""
    colorama.init(autoreset=True)

    # if sys.argv[1].casefold() == "-update":
    #     key = retrieve_key()
    #     token = retrieve_token()
    #     # filter_json = create_filter(
    #     #     key, token, "none", INCLUDE_DEFAULT + INCLUDE_QUESTION_TEST
    #     # )
    #     # filter_id = get_filter_id(filter_json)
    #     # print(filter_id)
    #     # Filter question test : !)GrKmj4SO9s6)An
    #     # Filter question :
    #     get_all_questions(key, token, filter="!)GrKmj4SO9s6)An")

    cmdline = parse_args(None)
    if not cmdline or not cmdline.action:
        raise Exception("Critical issue in parsing the command line")
    if cmdline.action == "check":
        client_id = retrieve_client_id()
        key = retrieve_key()
        token = retrieve_token()
        print_check_result(client_id, key, token)
    if cmdline.action == "auth":
        client_id = retrieve_client_id()
        get_authorization_url(client_id)
        get_access_token_from_url()


if __name__ == "__main__":
    main()
