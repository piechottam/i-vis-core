# pylint: disable=redefined-outer-name
from typing import Any, Optional, Sequence

import pytest
from _pytest.fixtures import SubRequest

from i_vis.core import blueprint as bp


@pytest.fixture
def pagination_params(request: SubRequest) -> bp.PaginationParameters:
    return bp.PaginationParameters(*request.param)


@pytest.fixture
def pager_info(request: SubRequest) -> bp.PagerInfo:
    return bp.PagerInfo(*request.param)


def test_pagination_parameters() -> None:
    pagination_params = bp.PaginationParameters(1, 2)
    assert pagination_params.current_id == 1
    assert pagination_params.size == 2


class TestPagerInfo:
    @pytest.mark.parametrize(
        "pagination_params,total,expected",
        [
            ((1, 1), None, None),
            ((1, 1), 10, 10),
            ((5, 2), 10, 5),
            ((6, 3), 10, 4),
            ((10, 5), 10, 2),
        ],
        indirect=("pagination_params",),
    )
    def test_pages(
        self,
        pagination_params: bp.PaginationParameters,
        total: Optional[int],
        expected: int,
    ) -> None:
        pager_info = bp.PagerInfo(pagination_params, total)
        assert pager_info.pages == expected


@pytest.mark.parametrize(
    "current_id,size,total,expected",
    [
        (1, 2, 4, 3),
        (2, 2, 4, None),
        (3, 2, 4, None),
        (4, 2, 4, None),
    ],
)
def test_next_id(
    current_id: int,
    size: int,
    total: int,
    expected: Optional[int],
) -> None:
    assert bp.get_next_id(current_id, size, total) == expected


@pytest.fixture
def list_obj() -> Sequence[int]:
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


@pytest.fixture
def list_pager() -> bp.ListPager:
    return bp.ListPager()


class TestListPager:
    @pytest.mark.parametrize(
        "current_id,size,expected",
        [
            (0, 2, [1, 2]),
            (2, 2, [3, 4]),
            (4, 2, [5, 6]),
            (6, 2, [7, 8]),
            (8, 2, [9, 10]),
            (10, 2, []),
            (0, 5, [1, 2, 3, 4, 5]),
            (5, 5, [6, 7, 8, 9, 10]),
            (10, 5, []),
        ],
    )
    def test_paginated_results(
        self,
        list_pager: bp.ListPager,
        list_obj: Sequence[int],
        current_id: int,
        size: int,
        expected: Sequence[Any],
    ) -> None:
        assert (
            list_pager.paginated_result(
                list_obj,
                bp.PaginationParameters(current_id=current_id, size=size),
            ).results
            == expected
        )
