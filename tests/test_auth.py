"""Tests for the stack_overflow_importer/auth.py module."""

import contextlib
import os
import re

import pytest
from stack_overflow_importer import auth


@contextlib.contextmanager
def override_env_variable(**kwargs):
    """Context manager that overrides environment variables.

    Params
    ------
        **kwargs : a dict of key value variables
    """
    backup = dict(os.environ)
    for key, value in kwargs.items():
        if value is None:
            if os.environ.get(key):
                del os.environ[key]
        else:
            os.environ[key] = value
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(backup)


class TestRetrieveClientID:
    """Tests for auth.retrieve_client_id()."""

    def test_key_exists(self):
        """Test for auth.retrieve_key() - when the key exists"""
        with override_env_variable(SO_IMPORTER_CLIENT_ID="test_client"):
            key = auth.retrieve_client_id()
            assert key == "test_client"

    def test_key_doesnt_exist(self):
        """Test for auth.retrieve_key() - when the key doesn't exists"""
        with override_env_variable(SO_IMPORTER_CLIENT_ID=None):
            key = auth.retrieve_client_id()
            assert key is None


class TestRetrieveKey:
    """Tests for auth.retrieve_key()."""

    def test_key_exists(self):
        """Test for auth.retrieve_key() - when the key exists"""
        with override_env_variable(SO_IMPORTER_KEY="test_key"):
            key = auth.retrieve_key()
            assert key == "test_key"

    def test_key_doesnt_exist(self):
        """Test for auth.retrieve_key() - when the key doesn't exists"""
        with override_env_variable(SO_IMPORTER_KEY=None):
            key = auth.retrieve_key()
            assert key is None


class TestRetrieveToken:
    """Tests for auth.retrieve_token()."""

    def test_ok(self):
        """Tests when the token exists."""
        with override_env_variable(SO_IMPORTER_TOKEN="test_token"):
            key = auth.retrieve_token()
            assert key == "test_token"

    def test_ko(self):
        """Tests when the token doesn't exists."""
        with override_env_variable(SO_IMPORTER_TOKEN=None):
            key = auth.retrieve_token()
            assert key is None


class TestGetAuthorizationURL:
    """Tests for auth.get_authorization_url()"""

    @pytest.mark.live
    def test_ok_actual_call(self):
        """Tests if the authorization returns a URL"""
        url, state = auth.get_authorization_url("12345")
        assert url is not None
        assert state is not None
        assert re.match(
            # pylint: disable=line-too-long
            r"https://stackexchange.com/oauth/dialog\?response_type=code\&client_id=\d+\&redirect_uri=https%3A%2F%2Fstackexchange\.com%2Foauth%2Flogin_success&scope=no_expiry&state=[a-zA-Z\d]*",
            url,
        )


class TestRetrieveEnvVariable:
    """Tests for auth.retrieve_env_variable()."""

    def test_ok(self):
        """Tests when the variable exists."""
        with override_env_variable(SO_DUMMY_TEST_VAR="test_var"):
            var = auth.retrieve_env_variable("SO_DUMMY_TEST_VAR")
            assert var == "test_var"

    def test_no_args(self, caplog):
        """Tests when the variable doesn't exists."""
        auth.retrieve_env_variable(None)
        assert "An environment variable name must be supplied" in caplog.records[0].msg

    def test_variable_doesnt_exist(self, caplog):
        """Tests when the variable doesn't exists."""
        auth.retrieve_env_variable("SO_DUMMY_TEST_VAR")
        assert "Couldn't find the environment variable." in caplog.records[0].msg


class TestGetAccessTokenFromUrl:
    """Tests for auth.get_access_token_from_url()"""

    def test_ok_input(self, monkeypatch, capsys):
        """tests if the method successfully extracts a token from an OK url."""
        # pylint: disable=line-too-long
        test_url = "https://stackexchange.com/oauth/login_success#access_token=AaBbCcDdEeFf123456))&state=ABCDEFG12345667"
        monkeypatch.setattr("builtins.input", lambda _: test_url)
        auth.get_access_token_from_url()
        captured = capsys.readouterr()
        assert (
            "The token is \x1b[32m\x1b[100mAaBbCcDdEeFf123456))\x1b[0m" in captured.out
        )


class TestExtractTokenFromUrL:
    """Tests for auth.get_access_token_from_url()"""

    # pylint: disable=line-too-long
    @pytest.mark.parametrize(
        "url, result, exception, message",
        [
            (
                None,
                None,
                ValueError,
                r"You must provide a URL to extract the token from it.",
            ),
            (
                "https://stackexchange.com/oauth/login_success#access_token=ABCDEFG))&state=iYRtyLfNE4tQXczucu5t0Y1yjvBlya",
                "ABCDEFG))",
                None,
                None,
            ),
            (
                "https://badurl.com/oauth/login_success#access_token=ABCDEFG))&state=iYRtyLfNE4tQXczucu5t0Y1yjvBlya",
                None,
                ValueError,
                r"The URL provided",
            ),
        ],
    )
    def test_parametrized_tokens(self, url, result, exception, message):
        """Tests token extraction on various kinds of urls."""
        if isinstance(exception, type) and issubclass(exception, Exception):
            with pytest.raises(exception, match=message):
                auth.extract_token_from_url(url)
        else:
            token = auth.extract_token_from_url(url)
            assert token == result
