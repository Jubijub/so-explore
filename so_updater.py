"""Script to auto update the question bank from Stack Exchange."""
from argparse import ArgumentParser
import sys
from typing import Any
import argparse
import json
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
from stack_overflow_importer.filters import QUESTION_TEST_FILTER_ID
from stack_overflow_importer.questions import get_questions


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


def build_args_parser() -> ArgumentParser:
    """Builds a parser that can process so_importer command line arguments.

    Returns
    -------
        an argparse ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Utility to import Stack overflow questions.",
    )
    subparsers = parser.add_subparsers(
        dest="action",
        help="desired action for this program.",
        required=True,
    )
    subparsers.add_parser(
        "check",
        help="checks that the StackExchange API keys and tokens are set properly.",
    )
    subparsers.add_parser(
        "auth",
        help="triggers the API authentication process to obtain an API token.",
    )

    parser_questions = subparsers.add_parser(
        "questions",
        help="retrieves Stack Overflow topics and update the result database.",
    )
    parser_questions.add_argument(
        "--filter",
        help="The hash of a filter, as provided by filters/create API method.",
    )
    parser_questions.add_argument(
        "--page",
        help=(
            "If results fit more than one page, which page to return. 1 is the first"
            " page."
        ),
        type=int,
    )
    parser_questions.add_argument(
        "--pagesize",
        help="Defines how many results to provide per page, between 0 and 100.",
        type=int,
    )
    parser_questions.add_argument(
        "--fromdate",
        help=(
            "Retrieve all questions from this date. If not supplied, will retrieve all"
            " questions."
        ),
    )
    parser_questions.add_argument(
        "--todate",
        help=(
            "Retrieve all questions until this date. If not supplied, will retrieve all"
            " questions until now."
        ),
    )
    parser_questions.add_argument(
        "--order",
        help="The order in which to sort the results.",
    )
    parser_questions.add_argument(
        "--min",
        help="For sort by activity/creation/votes, defines the minimum value to return",
    )
    parser_questions.add_argument(
        "--max",
        help="For sort by activity/creation/votes, defines the maximum value to return",
    )
    parser_questions.add_argument(
        "--sort",
        help=(
            "Which sorting method to use : activity, creation, votes, hot, week, month"
        ),
    )
    parser_questions.add_argument(
        "--tagged",
        help=(
            "Semi-colon delimited list of tags. Will return questions which match all"
            " tags."
        ),
    )
    return parser


def extract(obj: object, attribute: str, default: Any = None) -> str | None:
    """Utility to get an object attribute value in case the attribute exist but is None
    or in case the attribute doesn't exist. This is useful because getattr alone
    doesn't return the default if the attribute exists but is None."""
    try:
        result = getattr(obj, attribute)
        if result:
            return result
        if default:
            return str(default)

    except AttributeError:
        if default is None:
            return None
        return str(default)


def main():
    """Main logic."""
    colorama.init(autoreset=True)

    cmdline = build_args_parser().parse_args(None)
    if not cmdline or not cmdline.action:
        raise Exception("Critical issue in parsing the command line")

    try:
        match cmdline.action:
            case "check":
                client_id = retrieve_client_id()
                key = retrieve_key()
                token = retrieve_token()
                if all((client_id, key, token)):
                    so_logger.info(
                        "All the environment variables seem to be set correctly, and a"
                        " value has been retrieved for all of them."
                    )

            case "auth":
                client_id = retrieve_client_id()
                get_authorization_url(client_id)
                get_access_token_from_url()

            case "questions":
                key = retrieve_key()
                token = retrieve_token()
                response = get_questions(
                    key,
                    token,
                    extract(cmdline, "filter", QUESTION_TEST_FILTER_ID),
                    extract(cmdline, "page", 1),
                    extract(cmdline, "pagesize", 30),
                    extract(cmdline, "fromdate", None),
                    extract(cmdline, "todate", None),
                    extract(cmdline, "order", None),
                    extract(cmdline, "min", None),
                    extract(cmdline, "max", None),
                    extract(cmdline, "sort", None),
                    extract(cmdline, "tagged", None),
                )
                print(json.dumps(response, indent=2))
    # pylint: disable=broad-except
    except Exception:
        so_logger.critical("Fatal error", exc_info=True)


if __name__ == "__main__":
    main()
