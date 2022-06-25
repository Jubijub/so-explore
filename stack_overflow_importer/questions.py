""" Test script to access Stack overflow data """

from typing import Any
import datetime
import logging
from strenum import StrEnum
from stack_overflow_importer.base import query_method


so_logger = logging.getLogger("so_importer")


class Order(StrEnum):
    """Enum describing possible sort orders."""

    ASC = "asc"
    DESC = "desc"


class QuestionSortMethod(StrEnum):
    """Enum describing accepted sort methods for questions."""

    ACTIVITY = "activity"
    VOTES = "votes"
    CREATION = "creation"
    HOT = "hot"
    WEEK = "week"
    MONTH = "month"


DATE_BOUND_SORT = ("activity", "creation")
INT_BOUND_SORT = "vote"
NO_MINMAX_SORT = ("hot", "week", "month")


Timestampable = str | int | float | datetime.datetime | datetime.date
"""Type alias describing all the inputs which can be transformed into a timestamp"""


def extract_int(
    name: str, value: Any, upper: int | None = None, lower: int | None = None
) -> int:
    """Extracts an integer from any kind of compatible input, and ensures the integer
    conforms with the upper and lower bounds, if specified.

    Parameters
    ----------
        :name str: the name of the attribute. Will be used to format more detailed
        error messages.
        :value Any: the value from which to extract the int
        :upper int|None: optionnal upper bound
        :lower int|None: optionnal lower bound

    Returns
    -------
        Returns an int if it managed to extract it. Any other case will raise a
        ValueError exception.
    """
    if not value:
        raise ValueError(
            f"You must provide a value for the '{name}' argument. You provided"
            f" '{value}'."
        )

    try:
        int_value = int(value)
    except ValueError as exc:
        raise ValueError(
            f"The '{name}' provided is not valid : '{value}' is not a valid number.",
        ) from exc

    if lower and not isinstance(lower, int):
        raise ValueError(
            f"Lower bound for '{name}' must be an int, you provided '{value}'.",
        )

    if lower is not None and int_value < lower:
        raise ValueError(
            f"The '{name}' provided is not valid : '{value}' is lower than the"
            f" lower bound '{lower}'."
        )
    if upper and not isinstance(upper, int):
        raise ValueError(
            f"Upper bound for {name} must be an int, you provided '{value}'."
        )
    if upper is not None and int_value > upper:
        raise ValueError(
            f"The '{name}' provided is not valid : '{value}' is higher than the"
            f" upper bound '{upper}'."
        )
    return int_value


def extract_order(value: str | Order) -> str:
    """Extracts an order string (eg: `asc`) from any kind of compatible input, a str
    or an Order enum member.

    Parameters
    ----------
        :value str | Order: the value from which to extract the order

    Returns
    -------
        Returns a lowercase str if it managed to extract it. Any other case will raise a
        ValueError exception.
    """
    if not value:
        raise ValueError(
            "You must provide a value for the 'order' argument. You provided"
            f" '{value}'."
        )
    try:
        str_value = str(value).lower()
    except ValueError as exc:
        raise ValueError(
            f"The 'order' provided is not valid : '{value}' cannot be converted to a"
            " str.",
        ) from exc

    valid_orders = dict((item.value, item) for item in Order)
    if str_value in valid_orders:
        return str_value
    else:
        raise ValueError(
            f"The 'order' provided is not valid : '{value}' is not a valid order.",
        )


def extract_sort(value: str | QuestionSortMethod) -> str:
    """Extracts a Question sort method string (eg: `activity`) from any kind of
    compatible input, a str or a QuestionSortMethod enum member.

    Parameters
    ----------
        :value str | QuestionSortMethod: the value from which to extract the sort method.

    Returns
    -------
        Returns a lowercase str if it managed to extract it. Any other case will raise a
        ValueError exception.
    """
    if not value:
        raise ValueError(
            f"You must provide a value for the 'sort' argument. You provided '{value}'."
        )
    try:
        str_value = str(value).lower()
    except ValueError as exc:
        raise ValueError(
            f"The 'sort' provided is not valid : '{value}' cannot be converted to a"
            " str.",
        ) from exc
    valid_sorts = dict((item.value, item) for item in QuestionSortMethod)
    if str_value in valid_sorts:
        return str_value
    else:
        raise ValueError(
            f"The 'sort' provided is not valid : '{value}' is not a valid sort method.",
        )


def extract_timestamp(name: str, value: Timestampable) -> int:
    """Extracts a Unix Epoch timestamp from any kind of
    compatible input :
    - int : valid unix epoch timestamp
    - float : valid unix epoch timestamp
    - str :
        - valix unix epoch timestamp as a str
        - ISO 8601 date only
        - ISO 8601 datetime with offset (with or without milliseconds)
        - Note : it supports all the formats supported by datetime.fromisoformat()
    - datetime objects
    - date objects

    For date-like objects, the method assume the time to be 00:00:00:00000 UTC.

    Parameters
    ----------
        :value Timestampable: the value from which to extract the timestamp.

    Returns
    -------
        Returns a UTC Unix epoch timestamp as a str if it managed to extract it. Any other
        case will raise a ValueError exception.
    """
    if not value:
        raise ValueError(
            f"You must provide a value for the '{name}' argument. You provided"
            f" '{value}'."
        )

    timestamp = None
    if isinstance(value, (int, float)):
        try:
            datetime.datetime.fromtimestamp(value)
            timestamp = int(value)
        except ValueError as exc:
            raise ValueError(
                f"The '{name}' provided is not valid : '{value}' cannot be converted to"
                " a timestamp.",
            ) from exc
        except OverflowError as ovf:
            raise ValueError(
                f"The '{name}' provided is not valid : '{value}' is outside of "
                " normal bounds for a timestamp.",
            ) from ovf

    if isinstance(value, str):
        try:
            unaware = datetime.datetime.fromisoformat(value)
            aware = unaware.replace(tzinfo=datetime.timezone.utc)
            timestamp = int(aware.timestamp())
        except ValueError:
            try:
                datetime.datetime.fromtimestamp(int(value))
                timestamp = int(value)
            except ValueError as exc:
                raise ValueError(
                    f"The '{name}' provided is not valid : '{value}' couldn't be"
                    " converted into a date or a timestamp.",
                ) from exc

    if isinstance(value, datetime.date):
        try:
            roundeddatetime = datetime.datetime(
                value.year, value.month, value.day, 0, 0, 0, 0, datetime.timezone.utc
            )
            timestamp = int(roundeddatetime.timestamp())
        except ValueError:
            pass
    if isinstance(value, datetime.datetime):
        timestamp = int(value.timestamp())

    if timestamp is None:
        raise ValueError(
            f"The '{name}' provided is not valid : '{value}' couldn't be"
            " converted into a timestamp.",
        )

    return timestamp


def build_questions_params(
    filter: str | None = None,
    page: str | int | None = 1,
    pagesize: str | int | None = 30,
    fromdate: Timestampable | None = None,
    todate: Timestampable | None = None,
    order: str | Order | None = Order.DESC,
    # pylint: disable=redefined-builtin
    min: str | int | Timestampable | None = None,
    max: str | int | Timestampable | None = None,
    sort: str | QuestionSortMethod | None = QuestionSortMethod.ACTIVITY,
    tagged: str | None = None,
) -> dict:
    """Build a params dict for the `questions` method.

    Parameters
    ----------
        filter: Optional, the ID of a filter to use to restrict results. If None is
        provided, it will use the API default filter.

        page: Optional. If the number of results exceed 'pagesize', results will be
        paged. This indicates which page to retrieve. The default is 1.

        pagesize: Optional, the number of results to retrive per page. Between 0 and 100
        , default is 30.

        fromdate: results older than this epoch timestamp will be ignored. Accepts any
        of the following :
        - int : valid unix epoch timestamp
        - float : valid unix epoch timestamp
        - str :
            - valix unix epoch timestamp as a str
            - ISO 8601 date only
            - ISO 8601 datetime with offset (with or without milliseconds)
            - Note : it supports all the formats supported by datetime.fromisoformat()
        - datetime objects
        - date objects

        todate: results more recent than this epoch timestamp will be ignored. Accepts
        the same inputs as fromdate.

        order: determines in which order the results will be sorted. Default is DESC.

        min:
            - if `sort` is set to `score`, filters question with a score below min
            - if `sort` is set to `activity, creation`, filters the questions older than
                this epoch timestamp.
            - if `sort` is set to `hot, week, month`, min is ignored

        max:
            - if `sort` is set to `score`, filters question with a score above max
            - if `sort` is set to `activity, creation`, filters the questions more
            recent than this epoch timestamp.
            - if `sort` is set to `hot, week, month`, max is ignored

        sort: the method to use to sort the results. Can be any of QuestionSortMethod
        enum, or a str.

        tagged: string containing semi-colon separated tag names. Note : only results
        matching ALL the tags in the list will be returned.

    Returns
    -------
        a dict containing all the params
    """
    params = {"site": "stackoverflow"}
    if sort is not None:
        # Putting sort first as the processing of min/max depends on the sort value
        params["sort"] = str(extract_sort(sort))
    if filter is not None:
        params["filter"] = filter
    if page is not None:
        params["page"] = str(extract_int("page", page, lower=0))
    if pagesize is not None:
        params["pagesize"] = str(extract_int("pagesize", pagesize, lower=0, upper=100))
    if fromdate is not None:
        params["fromdate"] = str(extract_timestamp("fromdate", fromdate))
    if todate is not None:
        params["todate"] = str(extract_timestamp("todate", todate))
    if order is not None:
        params["order"] = str(extract_order(order))
    if min is not None:
        if sort:
            if sort in DATE_BOUND_SORT:
                params["min"] = str(extract_timestamp("min", min))
            if sort in INT_BOUND_SORT:
                params["min"] = str(extract_int("min", min))
            if sort in NO_MINMAX_SORT:
                so_logger.warning(
                    "The 'min' parameter %s was ignored as the sort parameter is"
                    " in %s.",
                    min,
                    NO_MINMAX_SORT,
                )
    if max is not None:
        if sort:
            if sort in DATE_BOUND_SORT:
                params["max"] = str(extract_timestamp("max", max))
            if sort in INT_BOUND_SORT:
                params["max"] = str(extract_int("max", max))
            if sort in NO_MINMAX_SORT:
                so_logger.warning(
                    "The 'max' parameter %s was ignored as the sort parameter is"
                    " in %s.",
                    max,
                    NO_MINMAX_SORT,
                )
    if tagged is not None:
        params["tagged"] = tagged

    return params


def get_questions(
    key: str | None = None,
    access_token: str | None = None,
    filter: str | None = None,
    page: str | int | None = None,
    pagesize: str | int | None = None,
    fromdate: Timestampable | None = None,
    todate: Timestampable | None = None,
    order: str | Order | None = None,
    # pylint: disable=redefined-builtin
    min: str | int | None = None,
    max: str | int | None = None,
    sort: str | QuestionSortMethod | None = None,
    tagged: str | None = None,
) -> dict | None:
    """Queries Stack Overflow API to retrieve questions.

    All parameters from the API are exposed and work as described here
     https://api.stackexchange.com/docs/questions.

    Parameters
    ----------
        key: the API key, provided by completing
    https://stackapps.com/apps/oauth/register registration.

        access_tocken: the API access token provided by granting this app access,
    by calling `get_access_token_from_url()`.

        filter : Optional, the ID of a filter to use to restrict results. If None is
    provided, it will use the API default filter.

        page: Optional, the page number to be retrieved.

        pagesize: Optional, the number of results to retrive per page. Between 0 and 100.

        fromdate: Optional, results older than this epoch timestamp will be ignored.

        todate: Optional, results more recent than this epoch timestamp will be ignored.

        order: Optional, determines in which order the results will be sorted. Default is DESC.

        min:
            - if `sort` is set to `score, hot, week, month`, filters question below min
            - if `sort` is set to `activity, creation`, filters the questions older than
             this epoch timestamp.

        max:
            - if `sort` is set to `score, hot, week, month`, filters question above max
            - if `sort` is set to `activity, creation`, filters the questions more
            recent than this epoch timestamp.

        sort: the method to use to sort the results. Can be any of QuestionSortMethod
        enum.

        tagged: string containing semi-colon separated tag names. Note : only results
        matching ALL tags in the list will be returned.

    """
    params = build_questions_params(
        filter, page, pagesize, fromdate, todate, order, min, max, sort, tagged
    )

    return query_method("questions", key, access_token, params)


# # pylint: disable=redefined-builtin
# def get_all_questions(key, access_token, filter=None):
#     """Access all questions."""
#     response = get_questions(
#         key,
#         access_token,
#         filter=filter,
#         fromdate=datetime.datetime(
#             2022, 1, 1, tzinfo=datetime.timezone.utc
#         ).timestamp(),
#         pagesize=1,
#         sort=QuestionSortMethod.CREATION,
#         order=Order.ASC,
#     )
#     if response:
#         print(f'Has more={response.get("has_more")}')

#     print(dumps(response, indent=2))

#     response = get_questions(
#         key,
#         access_token,
#         filter=filter,
#         fromdate=datetime.datetime(
#             2022, 1, 1, tzinfo=datetime.timezone.utc
#         ).timestamp(),
#         pagesize=1,
#         page=2,
#         sort=QuestionSortMethod.CREATION,
#         order=Order.ASC,
#     )
#     if response:
#         print(f'Has more={response.get("has_more")}')

#     print(dumps(response, indent=2))
