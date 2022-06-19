""" Test script to access Stack overflow data """

import datetime
from json import dumps
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


def build_questions_params(
    filter: str = None,
    page: int = None,
    pagesize: int = None,
    fromdate: int = None,
    todate: int = None,
    order: Order = None,
    # pylint: disable=redefined-builtin
    min: int = None,
    max: int = None,
    sort: QuestionSortMethod = None,
    tagged: str = None,
) -> dict:
    """Build a params dict for the `questions` method.

    Parameters
    ----------
        filter : Optional, the ID of a filter to use to restrict results. If None is
        provided, it will use the API default filter.

        page: Optional, the page number to be retrieved (default = 1).

        pagesize: Optional, the number of results to retrive per page. Between 0 and 100
        , default is 30.

        fromdate: results older than this epoch timestamp will be ignored.

        todate: results more recent than this epoch timestamp will be ignored.

        order: determines in which order the results will be sorted. Default is DESC.

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

    Returns
    -------
        a dict containing all the params
    """
    params = {"site": "stackoverflow"}
    if filter:
        params["filter"] = filter
    if page:
        if page < 1:
            so_logger.error(
                "The page number provided `%s` is not valid. It should be a number"
                " >= 1 ",
                page,
            )
            raise ValueError(
                f"The page number provided {page} is not valid. It should be a number"
                " >= 1 "
            )
        if not isinstance(page, int):
            so_logger.error(
                "The page number provided `%s` is not valid. It should be an integer",
                page,
            )
            raise ValueError(
                f"The page number provided {page} is not valid. It should be an integer"
            )
        params["page"] = page
    if pagesize:
        if pagesize < 1 or pagesize > 30:
            so_logger.error(
                "The pagesize number provided `%s` is not valid. It should be a number"
                " between 1 and 30.",
                pagesize,
            )
            raise ValueError(
                f"The pagesize number provided {pagesize} is not valid. It should be a"
                " number between 1 and 30."
            )
        if not isinstance(pagesize, int):
            so_logger.error(
                "The pagesize number provided `%s` is not valid. It should be an"
                " integer",
                page,
            )
            raise ValueError(
                f"The pagesize number provided {pagesize} is not valid. It should be an"
                " integer"
            )
        params["pagesize"] = pagesize
    if fromdate:
        try:
            _ = datetime.datetime.fromtimestamp(fromdate)
        except (ValueError, OverflowError) as exc:
            so_logger.error("The fromdate provided `%s` is not valid.", fromdate)
            raise ValueError from exc(
                f"The fromdate provided {fromdate} is not valid. It must be an epoch"
                " timestamp."
            )
        params["fromdate"] = str(int(fromdate))
    if todate:
        try:
            _ = datetime.datetime.fromtimestamp(todate)
        except (ValueError, OverflowError):
            so_logger.error("The todate provided `%s` is not valid.", todate)
            raise ValueError from exc(
                f"The todate provided {todate} is not valid. It must be an epoch"
                " timestamp."
            )
        params["todate"] = str(int(todate))
    if order:
        if not isinstance(order, Order):
            raise ValueError(
                f"The order provided {order} is not valid. It must be an instance of."
                " Order enum"
            )

        params["order"] = order.value
    if min:
        if not isinstance(min, int):
            raise ValueError(
                f"The min provided {min} is not valid. It must be an integer."
            )
        params["min"] = min
    if max:
        if not isinstance(max, int):
            raise ValueError(
                f"The max provided {max} is not valid. It must be an integer."
            )
        params["max"] = max
    if sort:
        if not isinstance(sort, QuestionSortMethod):
            raise ValueError(
                f"The sort method provided {sort} is not valid. It must be an instance "
                " of QuestionSortMethod"
            )

        params["sort"] = sort.value
    if tagged:
        params["tagged"] = tagged

    return params


def get_questions(
    key: str = None,
    access_token: str = None,
    filter: str = None,
    page: int = None,
    pagesize: int = None,
    fromdate: int = None,
    todate: int = None,
    order: Order = None,
    # pylint: disable=redefined-builtin
    min: int = None,
    max: int = None,
    sort: QuestionSortMethod = None,
    tagged: str = None,
):
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


# pylint: disable=redefined-builtin
def get_all_questions(key, access_token, filter=None):
    """Access all questions."""
    response = get_questions(
        key,
        access_token,
        filter=filter,
        fromdate=datetime.datetime(
            2022, 1, 1, tzinfo=datetime.timezone.utc
        ).timestamp(),
        pagesize=1,
        sort=QuestionSortMethod.CREATION,
        order=Order.ASC,
    )
    print(f'Has more={response.get("has_more")}')

    print(dumps(response, indent=2))

    response = get_questions(
        key,
        access_token,
        filter=filter,
        fromdate=datetime.datetime(
            2022, 1, 1, tzinfo=datetime.timezone.utc
        ).timestamp(),
        pagesize=1,
        page=2,
        sort=QuestionSortMethod.CREATION,
        order=Order.ASC,
    )
    print(f'Has more={response.get("has_more")}')

    print(dumps(response, indent=2))
