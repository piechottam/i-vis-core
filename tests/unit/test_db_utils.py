# pylint: disable=redefined-outer-name

from typing import Any, Type

import pytest

from i_vis.core import db_utils
from i_vis.core.db import db


@pytest.mark.parametrize(
    "fname,expected",
    [
        ("/tmp/TestTname.txt", "test_tname"),
        ("testTest", "test_test"),
    ],
)
def test_fname2tname(fname: str, expected: str) -> None:
    assert db_utils.fname2tname(fname) == expected


@pytest.fixture
def mini_mixin() -> Type[Any]:
    class Mixin1:
        pk = db.Column(db.String(30), primary_key=True)
        name = db.Column(db.String(30))
        type = db.Column(db.String(30), name="core")
        n = 10

    return Mixin1


def test_column_names(mini_mixin: Type[Any]) -> None:
    assert db_utils.column_names(mini_mixin) == ("pk", "name", "core")
