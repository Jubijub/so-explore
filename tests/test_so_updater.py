"""Test module for the script so_updater.py"""


import pytest
from so_updater import parse_args, print_check_result
from tests.test_auth import override_env_variable


class TestPrintCheckResults:
    """Tests for so_importer.print_check_results()"""

    @pytest.mark.parametrize(
        "args, message",
        [
            (
                ["test_key", "Test_client", "test_token"],
                r"All environment variables could be retrieved",
            ),
            (
                [None, "Test_client", "test_token"],
                r"The client_ID is missing",
            ),
            (
                ["test_key", None, "test_token"],
                r"The key is missing",
            ),
            (
                ["test_key", "Test_client", None],
                r"The OAuth token is missing",
            ),
        ],
    )
    def test_all_variables_ok(self, args, message, caplog):
        """Test that it displays a confirmation if all env variables are OK."""

        print_check_result(*args)
        assert message in caplog.records[0].msg


def test_parse_args_no_args(capsys):
    """Tests parse_args() with empty argv"""
    try:
        parse_args([])
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert "the following arguments are required: action" in captured.err


def test_parse_args_wrong_first_argument(capsys):
    """Tests parse_args() with empty argv"""
    try:
        parse_args(["so_updater.py"])
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert (
        "invalid choice: 'so_updater.py' (choose from 'check', 'auth', 'fetch')"
        in captured.err
    )


@pytest.mark.parametrize(
    "args, response, text",
    [
        (
            ["-h"],
            None,
            r"Utility to import Stack overflow questions.",
        ),
        (
            ["check"],
            {"action": "check"},
            r"",
        ),
        (
            ["auth"],
            {"action": "auth"},
            r"",
        ),
        (
            ["fetch"],
            {"action": "fetch"},
            r"",
        ),
    ],
)
def test_parse_args(capsys, args, response, text):
    """Tests the responses from various inputs to parse_args()"""
    try:
        cmdline = parse_args(args)
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert text in captured.out
    if response:
        for key, value in response.items():
            assert getattr(cmdline, key) is not None
            assert getattr(cmdline, key) == value
