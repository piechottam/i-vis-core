import pytest

from i_vis.core import db
from i_vis.core import db_utils


def test_read_db():
    pass


@pytest.mark.parametrize(
    "fname,expected",
    [
        ("/tmp/TestTname.txt", "test_tname"),
        ("testTest", "test_test"),
    ],
)
def test_fname2tname(fname, expected):
    assert db_utils.fname2tname(fname) == expected


class TestColumnNames:
    def test_empty(self):
        class TestMixin:
            pass

        assert db_utils.column_names(TestMixin) == []

    def test_mixed(self):
        class TestMixin:
            NAME = "VALUE"

            def test_column1(self):
                return db.Column()

            def test_column2(self):
                return db.Column()

            def test_other(self):
                return ["test"]

        assert db_utils.column_names(TestMixin) == [
            "test_column1",
            "test_column2",
        ]


def test_row_count():
    assert False
