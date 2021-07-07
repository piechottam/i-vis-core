# pylint: disable=redefined-outer-name

from typing import Any, Sequence, TYPE_CHECKING

import pytest

from i_vis.core import blueprint as bp
from i_vis.core.models import User


if TYPE_CHECKING:
    from i_vis.core.db import db as db_


@pytest.fixture
def query_pager() -> bp.QueryPager:
    return bp.QueryPager()


@pytest.fixture
def query_pager_model(db: "db_", list_obj: Sequence[int]) -> None:
    db.create_all()
    for i in list_obj:
        obj = User(
            id=i, name="name" + str(i), mail="mail" + str(i), password="password"
        )
        db.session.add(obj)
    db.session.commit()


@pytest.fixture
def list_obj() -> Sequence[int]:
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


class TestQueryPager:
    @pytest.mark.parametrize(
        "current_id,size,expected",
        [
            (1, 2, [1, 2]),
            (2, 2, [2, 3]),
            (4, 2, [4, 5]),
            (6, 2, [6, 7]),
            (8, 2, [8, 9]),
            (10, 2, [10]),
            (1, 5, [1, 2, 3, 4, 5]),
            (5, 5, [5, 6, 7, 8, 9]),
            (10, 5, [10]),
            (11, 5, []),
        ],
    )
    # pylint: disable=unused-argument
    def test_paginated_results(
        self,
        query_pager: bp.QueryPager,
        query_pager_model: None,
        current_id: int,
        size: int,
        expected: Sequence[Any],
    ) -> None:
        query_wrapper = bp.QueryWrapper(User.id, User.query)
        results = query_pager.paginated_result(
            query_wrapper,
            bp.PaginationParameters(current_id=current_id, size=size),
        ).results
        assert [result.id for result in results] == expected
