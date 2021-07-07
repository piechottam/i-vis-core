# pylint: disable=redefined-outer-name

from typing import TYPE_CHECKING

import pytest

from i_vis.core import db_utils
from i_vis.core.models import User

if TYPE_CHECKING:
    from i_vis.core.db import db as db_


# pylint: disable=unused-argument
def test_get_model(db: "db_") -> None:
    db.create_all()
    assert db_utils.get_model("users") == User


# pylint: disable=unused-argument
def test_get_model_fails(db: "db_") -> None:
    db.create_all()
    with pytest.raises(KeyError) as excinfo:
        _ = db_utils.get_model("unknown")
    assert excinfo.value.args == ("unknown",)


def test_row_count(db: "db_") -> None:
    db.create_all()
    assert db_utils.row_count("users") == 0

    db.session.add(User(name="name", mail="mail", password="password"))
    db.session.commit()

    assert db_utils.row_count("users") == 1
