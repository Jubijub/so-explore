"""Test module for ./stack_overflow_importer/so_importer.py."""

from datetime import datetime, timezone
import pytest
from stack_overflow_importer import questions


class TestBuildQuestionsParams:
    """Tests for so_importer.build_questions_params()."""

    @pytest.mark.parametrize(
        "field",
        [
            "filter",
            "page",
            "pagesize",
            "fromdate",
            "todate",
            "order",
            "min",
            "max",
            "sort",
            "tagged",
        ],
    )
    def test_lack_of_default_value(self, field):
        """Tests that a field not provided doesn't end up in the params object"""
        params = questions.build_questions_params()
        # pylint: disable=consider-iterating-dictionary
        assert field not in params.keys()

    def common_test(self, field, value, result, exception, exception_message):
        if isinstance(exception, type) and issubclass(exception, Exception):
            with pytest.raises(exception, match=exception_message):
                questions.build_questions_params(**{field: value})
        else:
            params = questions.build_questions_params(**{field: value})
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
            ("page", 0, None, ValueError, r"The page number provided 0 is not valid"),
            ("page", -1, None, ValueError, r"The page number provided -1 is not valid"),
            (
                "page",
                42.5,
                None,
                ValueError,
                r"The page number provided 42.5 is not valid",
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
                r"The pagesize number provided -1 is not valid",
            ),
            (
                "pagesize",
                99,
                None,
                ValueError,
                r"The pagesize number provided 99 is not valid",
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
                "1640991600",  # short ISO dates are not TZ aware
                None,
                None,
            ),
            (
                "fromdate",
                "foo",
                None,
                ValueError,
                r"The fromdate provided 'foo' is not a valid ISO 8601 date.",
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
                "1640991600",  # short ISO dates are not TZ aware
                None,
                None,
            ),
            (
                "todate",
                "foo",
                None,
                ValueError,
                r"The todate provided 'foo' is not a valid ISO 8601 date.",
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
            ("order", questions.Order.ASC, "asc", None, None),
            ("order", "desc", None, ValueError, None),
            ("min", None, None, None, None),
            ("min", 10, "10", None, None),
            ("min", "foo", None, ValueError, None),
            ("max", None, None, None, None),
            ("max", 50, "50", None, None),
            ("max", "foo", None, ValueError, None),
            ("sort", None, None, None, None),
            ("sort", questions.QuestionSortMethod.ACTIVITY, "activity", None, None),
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
            ("sort", questions.QuestionSortMethod.ACTIVITY, "activity", None, None),
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
