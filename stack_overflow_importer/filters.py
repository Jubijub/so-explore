"""Module handling Stack Exchange API filters."""

from stack_overflow_importer.base import query_method

INCLUDE_DEFAULT = (
    ".backoff;"
    ".error_id;"
    ".error_message;"
    ".error_name;"
    ".has_more;"
    ".items;"
    ".page;"
    ".page_size;"
    ".quota_max;"
    ".quota_remaining;"
    # ".total;"
)
INCLUDE_QUESTION = (
    "question.tags;"
    "question.is_answered;"
    "question.view_count;"
    "question.favourite_count;"
    "question.upvote_count;"
    "question.accepted_answer_id;"
    "question.answer_count;"
    "question.score;"
    "question.creation_date;"
    "question.id;"
    "question.link;"
    "question.title;"
    # 'question.body;'
)
INCLUDE_QUESTION_TEST = (
    # "question.tags;"
    # "question.is_answered;"
    # "question.view_count;"
    # "question.favourite_count;"
    # "question.upvote_count;"
    # "question.accepted_answer_id;"
    # "question.answer_count;"
    # "question.score;"
    "question.creation_date;"
    "question.id;"
    # "question.link;"
    "question.title;"
    # 'question.body;'
)


def create_filter(
    key: str,
    access_token: str,
    base: str,
    include: str = None,
    exclude: str = None,
    unsafe: bool = False,
) -> str:
    """Creates a custom filter for Stack Exchange API

    Useful context :
    https://api.stackexchange.com/docs/filters
    https://stackoverflow.com/questions/65687547/how-can-i-use-custom-filters-in-the-stack-exchange-api

    Parameters
    ----------
    key: the API key, provided by completing
    https://stackapps.com/apps/oauth/register registration

    access_tocken: the API access token provided by granting this app access,
    by calling `get_access_token_from_url()`

    base: name of a filter to use as a base for this new filter.

    include: a string of semicolon separated fields to include

    exclude: a string of semicolon separated fields to exclude

    unsafe: whether the filter can be unsafe or not (see Stack Exchange doc on Filters)

    Returns
    ----------
        a json string as returned by `filters/create` method

    """
    params = {}
    params["base"] = base
    if include:
        params["include"] = include
    if exclude:
        params["exclude"] = exclude
    params["unsafe"] = unsafe
    return query_method("filters/create", key, access_token, params)


def get_filter_id(filter_jason) -> str:
    """Extracts the filter ID from a create filter JSON response.

    Parameters
    ----------
        json: the json file as produced by `create_filter()`

    Returns
    ----------
        a string containing the filter ID, to be used to filter method calls.
    """
    if not filter_jason:
        return None
    return filter_jason.get("items")[0].get("filter")
