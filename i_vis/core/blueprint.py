""" Custom blueprint implementation.

`flask-smorest<https://github.com/marshmallow-code/flask-smorest>`_ is a REST API for flask and marshmallow.

The existing pagination implemention has been extended to support:
* keyset pagination and
* pagination info not in header.

Extended pagination can be used by using this custom :class:`Blueprint` implementation.
"""

import http
import math
from copy import deepcopy
from dataclasses import dataclass
from functools import wraps, cache
from typing import (
    Any,
    cast,
    Callable,
    Generic,
    MutableMapping,
    TypeVar,
    Mapping,
    Optional,
    Sequence,
    Union,
    TYPE_CHECKING
)

import flask_smorest
from flask_smorest.utils import unpack_tuple_response
from flask import request
from marshmallow import RAISE, EXCLUDE, post_load
from marshmallow.validate import Range
from webargs.flaskparser import FlaskParser
from sqlalchemy import Column
from .ma import ma

if TYPE_CHECKING:
    from sqlalchemy.orm import Query

#: Default values for pagination parameters
CURRENT_ID = 1

#: Default size of elements of a page
SIZE = 50

#: Maximum size of elements of a page
MAX_SIZE = 100


class StrictFlaskParser(FlaskParser):
    DEFAULT_UNKNOWN_BY_LOCATION = {
        "query": RAISE,
    }


class PaginationParameters:
    """Container for pagination parameters."""

    def __init__(self, current_id: int, size: int, max_size: int) -> None:
        self.current_id = current_id
        self.size = size
        self.max_size = max_size

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}, current_id={self.current_id}, size={self.size}, max_size={self.max_size}"


class PagerInfo:
    """Container for pager info."""

    def __init__(
            self,
            pagination_params: PaginationParameters,
            total: Optional[int] = None,
            next_id: Optional[int] = None,
    ) -> None:
        self.pagination_params = pagination_params
        self.total = total
        self.next_id = next_id

    @property
    def pages(self) -> Optional[int]:
        """Number of available pages.

        Returns:
            The number of available pages or None if total is not set.
        """

        if self.total is None:
            return None
        return math.ceil(self.total / self.pagination_params.size)


class PaginatedResult:
    def __init__(
            self,
            results: Sequence[Any],
            pager_info: PagerInfo,
            keys: Optional[Sequence[Any]] = None,
            links: Optional[Mapping[str, Any]] = None,
    ) -> None:
        self.keys = keys
        self.results = results
        self.pager_info = pager_info
        self.links = links

    @property
    def data(self) -> Union[Sequence[Any], Mapping[Any, Any]]:
        if self.keys:
            return dict(zip(self.keys, self.results))

        return self.results


T = TypeVar("T")


@cache
def create_pagination_args_schema(
        current_id_: int = CURRENT_ID,
        size_: int = SIZE,
        max_size_: int = MAX_SIZE,
) -> ma.Schema:
    class PaginationArgumentsSchema(ma.Schema):
        class Meta:
            ordered = True
            unknown = EXCLUDE

        current_id = ma.Integer(missing=current_id_)
        size = ma.Integer(
            missing=size_,
            validate=Range(min=1, max=max_size_),
        )
        max_size = ma.Constant(max_size_)

        @post_load
        # pylint: disable=no-self-use
        def make_parameters(
                self, data: Mapping[str, Any], **_kwargs: Any
        ) -> PaginationParameters:
            return PaginationParameters(
                current_id=data.get("current_id", current_id_),
                size=data.get("size", size_),
                max_size=data.get("max_size", max_size_),
            )

    return PaginationArgumentsSchema


class Pager(Generic[T]):
    """Abstract class for a pager."""

    def __init__(
            self,
            current_id: int = CURRENT_ID,
            size: int = SIZE,
            max_size: int = MAX_SIZE,
    ) -> None:
        self._current_id = current_id
        self._size = size
        self._max_size = max_size

    def create_schema(self) -> ma.Schema:
        return create_pagination_args_schema(
            self._current_id, self._size, self._max_size
        )

    def paginated_result(
            self, obj: T, parameters: PaginationParameters
    ) -> PaginatedResult:
        raise NotImplementedError


def get_next_id(current_id: int, size: int, total: int) -> Optional[int]:
    """Get next id.

    Assumes a simple list.

    Args:
        current_id: Current element index.
        size: Size of a page.
        total: Total elements.

    Returns:
        ``None``, if there is no next page.
    """
    if current_id < total:
        next_id = current_id + size
        if next_id < total:
            return next_id
    return None


@dataclass
class DictWrapper:
    #: Query that produces results to paginate
    results: Mapping[Any, Any]
    #: links
    links: MutableMapping[str, str]
    #: callback for links next key
    next_callback: Callable[[int], str]


class DictPager(Pager[DictWrapper]):
    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("current_id", 0)
        super().__init__(**kwargs)

    def paginated_result(
            self, obj: DictWrapper, parameters: PaginationParameters
    ) -> PaginatedResult:
        current_id = parameters.current_id
        size = parameters.size
        results = obj.results
        total = len(results)

        pager_info = PagerInfo(
            pagination_params=parameters,
            next_id=get_next_id(current_id, size, total),
            total=total,
        )

        links = dict(obj.links)
        if pager_info.next_id:
            links["next"] = obj.next_callback(pager_info.next_id)

        keys = list(results.keys())
        values = list(results.values())

        return PaginatedResult(
            results=values[current_id: (current_id + size)],
            keys=keys,
            pager_info=pager_info,
            links=links,
        )


@dataclass
class QueryWrapper:
    """Container for query pager."""

    #: Column used for pagination (keyset)
    column: Column[Any]
    #: Query that produces results to paginate
    query: "Query[Any]"
    #: links
    links: MutableMapping[str, str]
    #: callback next
    next_callback: Callable[[int], str]


class QueryPager(Pager[QueryWrapper]):
    """Query pager for SQLALCHEMY queries."""

    def paginated_result(
            self, obj: QueryWrapper, parameters: PaginationParameters
    ) -> PaginatedResult:
        # convenience
        column = obj.column
        query = obj.query
        current_id = parameters.current_id
        size = parameters.size
        total = query.count()  # TODO test might be slow
        next_id = None

        # process current elements - to be displayed
        results = (
            query.filter(column >= current_id)
                .order_by(column)
                .limit(size + 1)  # +1 to capture the next element
                .all()
        )
        if results and len(results) > size:
            # capture next element
            next_id = getattr(results[size], column.name, None)
            # remove next element from result
            results = results[slice(size)]

        pager_info = PagerInfo(
            pagination_params=parameters,
            total=total,
            next_id=next_id,
        )

        links = dict(obj.links)
        if pager_info.next_id:
            links["next"] = obj.next_callback(pager_info.next_id)

        return PaginatedResult(results=results, pager_info=pager_info, links=links)


class KeySetPaginationMixin:
    """KeySet pagination."""

    KEYSET_PAGINATION_PARSER = FlaskParser()

    @classmethod
    def _parse_request(cls, params_schema: ma.Schema) -> PaginationParameters:
        """TODO

        Args:
            params_schema:

        Returns:

        """

        return cast(
            PaginationParameters,
            KeySetPaginationMixin.KEYSET_PAGINATION_PARSER.parse(
                params_schema, request, location="query"
            ),
        )

    @classmethod
    def _add_api_doc(
            cls,
            wrapper: Callable[[Any], Any],
            params_schema: ma.Schema,
    ) -> None:
        """TODO

        Args:
            wrapper:
            params_schema:

        Returns:

        """

        error_status_code = Blueprint.ARGUMENTS_PARSER.DEFAULT_VALIDATION_STATUS

        # Add pagination params to doc info in wrapper object
        # pylint: disable=protected-access
        apidoc = deepcopy(getattr(wrapper, "_apidoc", {}))
        apidoc["pagination"] = {
            "parameters": {
                "in": "query",
                "schema": params_schema,
            },
            "response": {
                error_status_code: http.HTTPStatus(  # pylint: disable=no-member
                    error_status_code
                ).name,
            },
        }
        setattr(wrapper, "_apidoc", apidoc)

    def keyset_paginate(
            self,
            pager: Pager[T],
            current_id: int = CURRENT_ID,
            size: int = SIZE,
            max_size: int = MAX_SIZE,
    ) -> Callable[[Any], Any]:
        """TODO

        TODO :seealso: flask-smorest:pagination

        Args:
            pager: (Optional)
            current_id:
            size:
            max_size:

        Returns:
            Paginated date.
        """

        parameters_schema = pager.create_schema()

        def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                parameters = self._parse_request(parameters_schema)

                obj, status, headers = unpack_tuple_response(func(*args, **kwargs))
                paginated_result = pager.paginated_result(obj, parameters)
                return paginated_result, status, headers

            # TODO remove self._add_api_doc(wrapper, parameters_schema)
            return wrapper

        return decorator


class Blueprint(KeySetPaginationMixin, flask_smorest.Blueprint):
    """Extend flask_smorest.Blueprint with keyset pagination."""

    ARGUMENTS_PARSER = StrictFlaskParser()
