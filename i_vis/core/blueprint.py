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
from functools import wraps
from typing import (
    Any,
    Callable,
    Generic,
    TypeVar,
    Mapping,
    Optional,
    Sequence,
)

import flask_smorest
from flask_smorest.utils import unpack_tuple_response
from flask import request
from marshmallow import EXCLUDE, post_load
from marshmallow.validate import Range
from webargs.flaskparser import FlaskParser

from .db import db
from .ma import ma

#: Default values for pagination parameters
CURRENT_ID = 1

#: Default size of elements of a page
SIZE = 50

#: Maximum size of elements of a page
MAX_SIZE = 100


class PaginationParameters:
    """Container for pagination parameters."""

    def __init__(self, current_id: int, size: int) -> None:
        self.current_id = current_id
        self.size = size

    def __repr__(self) -> str:
        return "{}(current_id={!r},size={!r})".format(
            self.__class__.__name__, self.current_id, self.size
        )


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
    ) -> None:
        self.results = results
        self.pager_info = pager_info


T = TypeVar("T")


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

        @post_load
        # pylint: disable=unused-argument,no-self-use
        def make_parameters(
            self, data: Mapping[str, Any], **kwargs: Any
        ) -> PaginationParameters:
            return PaginationParameters(**data)

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


class ListPager(Pager[Sequence[Any]]):
    """Pager for list like containers."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("current_id", 0)
        super().__init__(**kwargs)

    def paginated_result(
        self, obj: Sequence[Any], parameters: PaginationParameters
    ) -> PaginatedResult:
        current_id = parameters.current_id
        size = parameters.size
        total = len(obj)

        pager_info = PagerInfo(
            pagination_params=parameters,
            next_id=get_next_id(current_id, size, total),
            total=total,
        )

        # fmt: off
        results = obj[current_id:(current_id + size)]
        # fmt: on

        return PaginatedResult(results=results, pager_info=pager_info)


@dataclass
class QueryWrapper:
    """Container for query pager."""

    #: Column used for pagination (keyset)
    column: db.Column
    #: Query that produces results to paginate
    query: db.Query


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

        return PaginatedResult(results=results, pager_info=pager_info)


class KeySetPaginationMixin:
    """KeySet pagination."""

    ARGUMENTS_PARSER = FlaskParser()

    @classmethod
    def _parse_request(cls, params_schema: ma.Schema) -> PaginationParameters:
        """TODO

        Args:
            params_schema:

        Returns:

        """
        return KeySetPaginationMixin.ARGUMENTS_PARSER.parse(
            params_schema, request, location="query"
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
        error_status_code = (
            KeySetPaginationMixin.ARGUMENTS_PARSER.DEFAULT_VALIDATION_STATUS
        )

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
        pager: Optional[Pager[T]] = None,
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

        if pager:
            parameters_schema = pager.create_schema()
        else:
            parameters_schema = create_pagination_args_schema(
                current_id, size, max_size
            )

        def decorator(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                parameters = self._parse_request(parameters_schema)

                if pager is None:
                    kwargs["pagination_params"] = parameters

                obj, status, headers = unpack_tuple_response(func(*args, **kwargs))

                if pager is None:
                    paginated_result = obj
                else:
                    paginated_result = pager.paginated_result(obj, parameters)

                results = {
                    "data": paginated_result.results,
                    "pager_info": paginated_result.pager_info,
                    "links": {},
                }
                return results, status, headers

            self._add_api_doc(wrapper, parameters_schema)
            return wrapper

        return decorator


class Blueprint(KeySetPaginationMixin, flask_smorest.Blueprint):
    """Extend flask_smorest.Blueprint with keyset pagination."""
