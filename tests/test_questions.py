"""Test module for ./stack_overflow_importer/so_importer.py."""

from datetime import date, datetime, timezone
import pytest
from stack_overflow_importer.questions import (
    Order,
    QuestionSortMethod,
    build_questions_params,
    extract_int,
    extract_order,
    extract_sort,
    extract_timestamp,
)


class TestExtractInt:
    """Tests for questions.extract_int()"""

    @pytest.mark.parametrize(
        "name, value, lower, upper, expected",
        [
            ("argument", 42, None, None, 42),
            ("argument", 42, 0, None, 42),
            ("argument", 42, None, 99, 42),
            ("argument", "42", None, None, 42),
            ("argument", "42", 0, None, 42),
            ("argument", "42", None, 99, 42),
            ("argument", 42.0, None, None, 42),
        ],
    )
    def test_valid_cases(self, name, value, lower, upper, expected):
        """GIVEN a valid int
        SHOULD return that int"""
        result = extract_int(name, value, upper, lower)
        assert result == expected

    @pytest.mark.parametrize(
        "name, value, lower, upper, message",
        [
            (
                "argument",
                None,
                None,
                None,
                (
                    r"You must provide a value for the 'argument' argument. You"
                    r" provided 'None'."
                ),
            ),
            (
                "argument",
                42,
                99,
                None,
                (
                    r"The 'argument' provided is not valid : '42' is lower than the"
                    r" lower bound '99'"
                ),
            ),
            (
                "argument",
                "42",
                99,
                None,
                (
                    r"The 'argument' provided is not valid : '42' is lower than the"
                    r" lower bound '99'"
                ),
            ),
            (
                "argument",
                42,
                None,
                0,
                (
                    r"The 'argument' provided is not valid : '42' is higher than the"
                    r" upper bound '0'"
                ),
            ),
            (
                "argument",
                "42",
                None,
                0,
                (
                    r"The 'argument' provided is not valid : '42' is higher than the"
                    r" upper bound '0'"
                ),
            ),
            (
                "argument",
                "LOL",
                None,
                None,
                r"The 'argument' provided is not valid : 'LOL' is not a valid number.",
            ),
        ],
    )
    def test_wrong_cases(self, name, value, lower, upper, message):
        """GIVEN a bad input
        SHOULD raise an exception"""
        with pytest.raises(ValueError, match=(message)):
            extract_int(name, value, upper, lower)


class TestExtractOrder:
    """Tests for questions.extract_order()"""

    @pytest.mark.parametrize(
        "value, expected",
        [
            ("asc", "asc"),
            ("desc", "desc"),
            ("ASC", "asc"),
            ("Desc", "desc"),
            (Order.ASC, "asc"),
            (Order.DESC, "desc"),
        ],
    )
    def test_valid_cases(self, value, expected):
        """GIVEN a valid order input
        SHOULD return that input as a lowercase string."""
        result = extract_order(value)
        assert result == expected

    @pytest.mark.parametrize(
        "value, message",
        [
            (
                None,
                (
                    r"You must provide a value for the 'order' argument. You"
                    r" provided 'None'."
                ),
            ),
            (
                "descending",
                (
                    r"The 'order' provided is not valid : 'descending' is not a valid"
                    r" order."
                ),
            ),
            (
                0,
                r"You must provide a value for the 'order' argument. You provided '0'.",
            ),
            (1, r"The 'order' provided is not valid : '1' is not a valid order."),
            (
                "",
                r"You must provide a value for the 'order' argument. You provided ''.",
            ),
        ],
    )
    def test_wrong_cases(self, value, message):
        """GIVEN a bad order input
        SHOULD raise an exception."""
        with pytest.raises(ValueError, match=(message)):
            extract_order(value)


class TestExtractSort:
    """Tests for questions.extract_sort()"""

    @pytest.mark.parametrize(
        "value, expected",
        [
            ("activity", "activity"),
            ("votes", "votes"),
            ("CREATION", "creation"),
            ("Hot", "hot"),
            ("week", "week"),
            ("MONTH", "month"),
            (QuestionSortMethod.ACTIVITY, "activity"),
            (QuestionSortMethod.VOTES, "votes"),
        ],
    )
    def test_valid_cases(self, value, expected):
        """GIVEN a valid order input
        SHOULD return that input as a lowercase string."""
        result = extract_sort(value)
        assert result == expected

    @pytest.mark.parametrize(
        "value, message",
        [
            (
                None,
                (
                    r"You must provide a value for the 'sort' argument. You"
                    r" provided 'None'."
                ),
            ),
            (
                "vote",
                (
                    r"The 'sort' provided is not valid : 'vote' is not a valid"
                    r" sort method."
                ),
            ),
            (
                0,
                r"You must provide a value for the 'sort' argument. You provided '0'.",
            ),
            (1, r"The 'sort' provided is not valid : '1' is not a valid sort method."),
            (
                "",
                r"You must provide a value for the 'sort' argument. You provided ''.",
            ),
        ],
    )
    def test_wrong_cases(self, value, message):
        """GIVEN a bad order input
        SHOULD raise an exception."""
        with pytest.raises(ValueError, match=(message)):
            extract_sort(value)


class TestExtractTimestamp:
    """Tests for questions.extract_timestamp()"""

    @pytest.mark.parametrize(
        "value, expected",
        [
            (1640995200, 1640995200),  # int
            (1640995200.0, 1640995200),  # float
            ("1640995200", 1640995200),  # str
            ("2022-01-01", 1640995200),  # ISO 8601 date
            # not supported("2022-01-01T00:00:00Z", 1640995200),  # ISO 8601 date with timezone
            ("2022-01-01T00:00:00+00:00", 1640995200),  # ISO 8601 date with offset
            ("2022-01-01T00:00:00.000000+00:00", 1640995200),
            (datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp(), 1640995200),
            (datetime(2022, 1, 1, tzinfo=timezone.utc), 1640995200),
            (date(2022, 1, 1), 1640995200),  # date
        ],
    )
    def test_valid_cases(self, value, expected):
        """GIVEN a valid Timestampable input
        SHOULD return a valid timestamp"""
        result = extract_timestamp("argument", value)
        assert result == expected

    @pytest.mark.parametrize(
        "name, value, message",
        [
            (
                "argument",
                None,
                (
                    r"You must provide a value for the 'argument' argument. You"
                    r" provided 'None'."
                ),
            ),
            (
                "argument",
                0,
                r"You must provide a value for the 'argument' argument. You provided"
                r" '0'.",
            ),
            (
                "argument",
                "",
                r"You must provide a value for the 'argument' argument. You provided"
                r" ''.",
            ),
            (
                "argument",
                "foo",
                r"The 'argument' provided is not valid : 'foo' couldn't be converted"
                r" into a date or a timestamp.",
            ),
        ],
    )
    def test_wrong_cases(self, name, value, message):
        """GIVEN an invalid Timestampable input
        SHOULD raise an exception."""
        with pytest.raises(ValueError, match=(message)):
            extract_timestamp(name, value)


class TestBuildQuestionsParams:
    """Tests for questions.build_questions_params()."""

    @pytest.mark.parametrize(
        "field",
        [
            "filter",
            "fromdate",
            "todate",
            "min",
            "max",
            "tagged",
        ],
    )
    def test_lack_of_default_value(self, field):
        """Tests that a field not provided doesn't end up in the params object"""
        params = build_questions_params()
        # pylint: disable=consider-iterating-dictionary
        assert field not in params.keys()

    def common_test(self, field, value, result, exception, exception_message):
        if isinstance(exception, type) and issubclass(exception, Exception):
            with pytest.raises(exception, match=exception_message):
                build_questions_params(**{field: value})
        else:
            params = build_questions_params(**{field: value})
            assert params.get(field) == result

    @pytest.mark.parametrize(
        "field, value, result, exception, exception_message",
        [
            ("filter", None, None, None, None),
            ("filter", "TEST", "TEST", None, None),
        ],
    )
    def test_build_params_filter(
        self, field, value, result, exception, exception_message
    ):
        """Creates a valid set of params given various filter values."""
        self.common_test(field, value, result, exception, exception_message)

    @pytest.mark.parametrize(
        "field, value, result, exception, exception_message",
        [
            ("page", None, None, None, None),
            ("page", 30, "30", None, None),
            ("page", 42.5, "42", None, None),
            (
                "page",
                0,
                None,
                ValueError,
                r"You must provide a value for the 'page' argument. You provided '0'.",
            ),
            (
                "page",
                -1,
                None,
                ValueError,
                r"The 'page' provided is not valid : '-1' is lower than the lower bound"
                r" '0'.",
            ),
        ],
    )
    def test_build_params_page(
        self, field, value, result, exception, exception_message
    ):
        """Creates a valid set of params given various page values."""
        self.common_test(field, value, result, exception, exception_message)

    @pytest.mark.parametrize(
        "field, value, result, exception, exception_message",
        [
            ("pagesize", None, None, None, None),
            ("pagesize", 10, "10", None, None),
            (
                "pagesize",
                -1,
                None,
                ValueError,
                r"The 'pagesize' provided is not valid : '-1' is lower than the lower"
                r" bound '0'.",
            ),
            (
                "pagesize",
                120,
                None,
                ValueError,
                r"The 'pagesize' provided is not valid : '120' is higher than the upper"
                r" bound '100'.",
            ),
        ],
    )
    def test_build_params_pagesize(
        self, field, value, result, exception, exception_message
    ):
        """Creates a valid set of params given various pagesize values."""
        self.common_test(field, value, result, exception, exception_message)

    @pytest.mark.parametrize(
        "field, value, result, exception, exception_message",
        [
            ("fromdate", None, None, None, None),
            (
                "fromdate",
                # returns a float
                datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp(),
                "1640995200",
                None,
                None,
            ),
            (
                "fromdate",
                1640995200,
                "1640995200",
                None,
                None,
            ),
            (
                "fromdate",
                "2022-01-01T00:00:00.000000+00:00",
                "1640995200",
                None,
                None,
            ),
            (
                "fromdate",
                "2022-01-01",
                "1640995200",  # short ISO dates are not TZ aware
                None,
                None,
            ),
            (
                "fromdate",
                "foo",
                None,
                ValueError,
                r"The 'fromdate' provided is not valid : 'foo' couldn't be converted"
                r" into a date or a timestamp.",
            ),
        ],
    )
    def test_build_params_fromdate(
        self, field, value, result, exception, exception_message
    ):
        """Creates a valid set of params given various fromdate values."""
        self.common_test(field, value, result, exception, exception_message)

    @pytest.mark.parametrize(
        "field, value, result, exception, exception_message",
        [
            ("todate", None, None, None, None),
            (
                "todate",
                # returns a float
                datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp(),
                "1640995200",
                None,
                None,
            ),
            (
                "todate",
                1640995200,
                "1640995200",
                None,
                None,
            ),
            (
                "todate",
                "2022-01-01T00:00:00.000000+00:00",
                "1640995200",
                None,
                None,
            ),
            (
                "todate",
                "2022-01-01",
                "1640995200",
                None,
                None,
            ),
            (
                "todate",
                "foo",
                None,
                ValueError,
                r"The 'todate' provided is not valid : 'foo' couldn't be converted into"
                r" a date or a timestamp.",
            ),
        ],
    )
    def test_build_params_todate(
        self, field, value, result, exception, exception_message
    ):
        """Creates a valid set of params given various todate values."""
        self.common_test(field, value, result, exception, exception_message)

    @pytest.mark.parametrize(
        "field, value, result, exception, exception_message",
        [
            ("order", None, None, None, None),
            ("order", Order.ASC, "asc", None, None),
            ("min", None, None, None, None),
            ("min", 10, "10", None, None),
            ("min", "foo", None, ValueError, None),
            ("max", None, None, None, None),
            ("max", 50, "50", None, None),
            ("max", "foo", None, ValueError, None),
            ("sort", None, None, None, None),
            ("sort", QuestionSortMethod.ACTIVITY, "activity", None, None),
            ("tagged", None, None, None, None),
            ("tagged", "python;pandas", "python;pandas", None, None),
        ],
    )
    def test_build_params_order(
        self, field, value, result, exception, exception_message
    ):
        """Creates a valid set of params given various order values."""
        self.common_test(field, value, result, exception, exception_message)

    @pytest.mark.parametrize(
        "field, value, result, exception, exception_message",
        [
            ("min", None, None, None, None),
            ("min", 10, "10", None, None),
            ("min", "foo", None, ValueError, None),
        ],
    )
    def test_build_params_min(self, field, value, result, exception, exception_message):
        """Creates a valid set of params given various min values."""
        self.common_test(field, value, result, exception, exception_message)

    @pytest.mark.parametrize(
        "field, value, result, exception, exception_message",
        [
            ("max", None, None, None, None),
            ("max", 50, "50", None, None),
            ("max", "foo", None, ValueError, None),
        ],
    )
    def test_build_params_max(self, field, value, result, exception, exception_message):
        """Creates a valid set of params given various max values."""
        self.common_test(field, value, result, exception, exception_message)

    @pytest.mark.parametrize(
        "field, value, result, exception, exception_message",
        [
            ("sort", None, None, None, None),
            ("sort", QuestionSortMethod.ACTIVITY, "activity", None, None),
        ],
    )
    def test_build_params_sort(
        self, field, value, result, exception, exception_message
    ):
        """Creates a valid set of params given various sort values."""
        self.common_test(field, value, result, exception, exception_message)

    @pytest.mark.parametrize(
        "field, value, result, exception, exception_message",
        [
            ("tagged", None, None, None, None),
            ("tagged", "python;pandas", "python;pandas", None, None),
        ],
    )
    def test_build_params_tagged(
        self, field, value, result, exception, exception_message
    ):
        """Creates a valid set of params given various tagged values."""
        self.common_test(field, value, result, exception, exception_message)
