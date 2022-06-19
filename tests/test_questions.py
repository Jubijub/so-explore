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

    @pytest.mark.parametrize(
        "field, value, exception, message",
        [
            ("filter", None, None, None),
            ("filter", "TEST", "TEST", None),
            ("page", None, None, None),
            ("page", 30, 30, None),
            ("page", -1, ValueError, r"The page number provided -1 is not valid"),
            ("page", 42.5, ValueError, r"The page number provided 42.5 is not valid"),
            ("pagesize", None, None, None),
            ("pagesize", 10, 10, None),
            (
                "pagesize",
                -1,
                ValueError,
                r"The pagesize number provided -1 is not valid",
            ),
            (
                "pagesize",
                99,
                ValueError,
                r"The pagesize number provided 99 is not valid",
            ),
            ("fromdate", None, None, None),
            (
                "fromdate",
                datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp(),
                "1640995200",
                None,
            ),
            ("fromdate", "foo", TypeError, None),
            ("todate", None, None, None),
            (
                "todate",
                datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp(),
                "1640995200",
                None,
            ),
            ("todate", "foo", TypeError, None),
            ("order", None, None, None),
            ("order", questions.Order.ASC, "asc", None),
            ("order", "desc", ValueError, None),
            ("min", None, None, None),
            ("min", 10, 10, None),
            ("min", "foo", ValueError, None),
            ("max", None, None, None),
            ("max", 50, 50, None),
            ("max", "foo", ValueError, None),
            ("sort", None, None, None),
            ("sort", questions.QuestionSortMethod.ACTIVITY, "activity", None),
            ("tagged", None, None, None),
            ("tagged", "python;pandas", "python;pandas", None),
        ],
    )
    def test_all_fields(self, field, value, exception, message):
        """Tests build_questions_params for good and bad inputs."""
        if isinstance(exception, type) and issubclass(exception, Exception):
            with pytest.raises(exception, match=message):
                questions.build_questions_params(**{field: value})
        else:
            params = questions.build_questions_params(**{field: value})
            assert params.get(field) == exception
