"""Tests for the stack_overflow_importer/auth.py module."""

import logging
import re

import pytest
from stack_overflow_importer import auth


class TestRetrieveEnvVariable:
    """Tests for auth.retrieve_env_variable()."""

    def test_ok(self, monkeypatch):
        """Tests when the variable exists."""
        monkeypatch.setenv("SO_DUMMY_TEST_VAR", "test_var")
        var = auth.retrieve_env_variable("SO_DUMMY_TEST_VAR")
        assert var == "test_var"

    def test_no_args(self, caplog):
        """Tests when the variable doesn't exists."""
        auth.retrieve_env_variable(None)
        assert "An environment variable name must be supplied" in caplog.records[0].msg

    def test_variable_doesnt_exist(self, monkeypatch, caplog):
        """Tests when the variable doesn't exists."""
        monkeypatch.delenv("SO_DUMMY_TEST_VAR", raising=False)
        auth.retrieve_env_variable("SO_DUMMY_TEST_VAR")
        assert caplog.record_tuples == [
            (
                "so_importer",
                logging.ERROR,
                "Couldn't find the environment variable SO_DUMMY_TEST_VAR.",
            )
        ]


class TestRetrieveClientID:
    """Tests for auth.retrieve_client_id()."""

    def test_key_exists(self, monkeypatch):
        """Test for auth.retrieve_key() - when the key exists"""
        monkeypatch.setenv("SO_IMPORTER_CLIENT_ID", "test_client")
        key = auth.retrieve_client_id()
        assert key == "test_client"

    def test_key_doesnt_exist(self, monkeypatch, caplog):
        """Test for auth.retrieve_key() - when the key doesn't exists"""
        monkeypatch.delenv("SO_IMPORTER_CLIENT_ID", raising=False)
        key = auth.retrieve_client_id()
        assert key is None
        assert "The Client ID is missing" in caplog.text


class TestRetrieveKey:
    """Tests for auth.retrieve_key()."""

    def test_key_exists(self, monkeypatch):
        """Test for auth.retrieve_key() - when the key exists"""
        monkeypatch.setenv("SO_IMPORTER_KEY", "test_key")
        key = auth.retrieve_key()
        assert key == "test_key"

    def test_key_doesnt_exist(self, monkeypatch, caplog):
        """Test for auth.retrieve_key() - when the key doesn't exists"""
        monkeypatch.delenv("SO_IMPORTER_KEY", raising=False)
        key = auth.retrieve_key()
        assert key is None
        assert "The key is missing" in caplog.text


class TestRetrieveToken:
    """Tests for auth.retrieve_token()."""

    def test_token_exists(self, monkeypatch):
        """Tests when the token exists."""
        monkeypatch.setenv("SO_IMPORTER_TOKEN", "test_token")
        key = auth.retrieve_token()
        assert key == "test_token"

    def test_key_doesnt_exist(self, monkeypatch, caplog):
        """Tests when the token doesn't exists."""
        monkeypatch.delenv("SO_IMPORTER_TOKEN", raising=False)
        key = auth.retrieve_token()
        assert key is None
        assert "The OAuth token is missing" in caplog.text


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
