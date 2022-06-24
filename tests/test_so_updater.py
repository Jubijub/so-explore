"""Test module for the script so_updater.py"""

import pytest
from so_updater import parse_args


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
