"""Test module for the script so_updater.py"""

import re
import pytest
from so_updater import build_args_parser


def valid_args_tester(args, expected) -> bool:
    """Helper to test valid arguments : arguments are expected
    to show up as attributes of the response.
    SystemExit should NOT be raised.

    Returns
    -------
        True if the test was passed, False otherwise"""
    if not (args and expected):
        return False
    try:
        namespace = build_args_parser().parse_args(args)
        assert namespace
        if expected and namespace:
            for key, value in expected.items():
                assert getattr(namespace, key) is not None
                assert getattr(namespace, key) == value
        return True
    except SystemExit:
        return False


def wrong_args_tester(args, message, capsys) -> bool:
    """Helper to test wrong arguments :
    - SystemExist will be raised
    - An error message should be displayed

    Returns
    -------
        True if the test was passed, False otherwise"""
    if args is None and message is None:
        return False
    try:
        build_args_parser().parse_args(args)
        return False
    except SystemExit:
        captured = capsys.readouterr()
        displayed = captured.err
        if not displayed:
            displayed = captured.out

        regex = re.compile(message)
        assert regex.search(displayed)
        return True


class TestBuildArgsParser:
    """Tests for so_updater.build_args_parser()"""

    def test_no_args(self, capsys):
        """GIVEN the generater parser
        GIVEN no arguments
        SHOULD fail and print that at least 1 argument is required"""
        assert wrong_args_tester(
            [],
            r"^usage: \w*\.py\s\[-h\] \{check,auth,questions\}",
            # error looks like :
            # usage: so_updater.py [-h] {check,auth,questions} ...
            # so_updater.py: error: the following arguments are required: action
            capsys,
        )

    def test_default_help(self, capsys):
        """GIVEN the generated parser
        GIVEN the `-h` argument
        SHOULD display the default help message."""
        assert wrong_args_tester(
            ["-h"], r"Utility to import Stack overflow questions", capsys
        )

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["check"],
                {"action": "check"},
            ),
            (
                ["auth"],
                {"action": "auth"},
            ),
            (
                ["questions"],
                {"action": "questions"},
            ),
        ],
    )
    def test_valid_actions(self, args, expected):
        """GIVEN the generated parser
        GIVEN a valid action parameter
        SHOULD recognize the parameter and produce a valid namespace"""
        assert valid_args_tester(args, expected)

    def test_wrong_first_argument(self, capsys):
        """GIVEN the generated parser
        GIVEN a wrong first argument
        SHOULD fail and prompt possible actions"""
        assert wrong_args_tester(
            ["WRONG"],
            r"^usage: \w*\.py\s\[-h\]"
            r" \{check,auth,questions\}[\s\S\w]*'WRONG'\s\(choose from 'check', 'auth',"
            r" 'questions'\)",
            # error looks like :
            # usage: so_updater.py [-h] {check,auth,questions} ...
            # so_updater.py: error: argument action: invalid choice: 'WRONG'
            #        (choose from 'check', 'auth', 'questions')
            capsys,
        )


class TestBuildArgsParserQuestions:
    """Tests for so_updater.build_args_parser(), specifically
    if the first action parameter is `questions`"""

    @pytest.mark.parametrize(
        "args, expected",
        [
            (
                ["questions", "--filter", "foo"],
                {"action": "questions", "filter": "foo"},
            ),
            (
                ["questions", "--page", "12"],
                {"action": "questions", "page": 12},
            ),
            (
                ["questions", "--pagesize", "21"],
                {"action": "questions", "pagesize": 21},
            ),
            (
                ["questions", "--fromdate", "foo"],
                {"action": "questions", "fromdate": "foo"},
            ),
            (
                ["questions", "--todate", "foo"],
                {"action": "questions", "todate": "foo"},
            ),
            (
                ["questions", "--order", "foo"],
                {"action": "questions", "order": "foo"},
            ),
            (
                ["questions", "--min", "foo"],
                {"action": "questions", "min": "foo"},
            ),
            (
                ["questions", "--max", "foo"],
                {"action": "questions", "max": "foo"},
            ),
            (
                ["questions", "--sort", "foo"],
                {"action": "questions", "sort": "foo"},
            ),
            (
                ["questions", "--tagged", "foo"],
                {"action": "questions", "tagged": "foo"},
            ),
        ],
    )
    def test_valid_questions_arguments(self, args, expected):
        """GIVEN the generated parser
        GIVEN the 'fetch' action parameter
        GIVEN a valid fetch argument
        SHOULD recognize the parameter and produce a valid namespace"""
        assert valid_args_tester(args, expected)

    def test_wrong_questions_argument(self, capsys):
        """GIVEN the generated parser
        GIVEN the `questions` action
        GIVEN a wrong argument
        SHOULD fail and prompt possible actions"""
        assert wrong_args_tester(
            ["questions", "--LOL"],
            r"unrecognized arguments: --LOL",
            # error looks like :
            # usage: so_updater.py [-h] {check,auth,questions} ...
            # so_updater.py: error: unrecognized arguments: --LOL
            capsys,
        )
