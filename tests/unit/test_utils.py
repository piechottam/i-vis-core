# pylint: disable=redefined-outer-name
from enum import Enum
from typing import Type, Sequence

import pytest

from i_vis.core import utils


def test_is_safe_url() -> None:
    assert False


class _EnumInstance(utils.EnumMixin, Enum):
    VAR1 = "VAL1"
    VAR2 = "VAL2"


@pytest.fixture
def enum_instance() -> Type[_EnumInstance]:
    return _EnumInstance


class TestEnumMixin:
    def test_from_str(self, enum_instance: Type[_EnumInstance]) -> None:
        assert enum_instance.from_str("VAL1") == enum_instance.VAR1
        assert enum_instance.from_str("VAL2") == enum_instance.VAR2

    def test_values(self, enum_instance: Type[_EnumInstance]) -> None:
        assert enum_instance.values() == {"VAL1", "VAL2"}


def test_datatable_columns() -> None:
    # TODO-report
    assert False


def test_datatable_render_link() -> None:
    # TODO-report
    assert False


def test_render_link() -> None:
    # TODO-report
    assert (
        utils.render_link("url_value", "label_value")
        == '<a href="url_value">label_value</a>'
    )


def test_register_datatable_query() -> None:
    # TODO-report
    assert False


def test_register_autocomplete() -> None:
    # TODO-report
    assert False


@pytest.mark.parametrize(
    "strs,expected",
    [
        (
            [
                "Cancer-Type",
            ],
            "CancerType",
        ),
        (
            [
                "Result",
                "Schema",
            ],
            "ResultSchema",
        ),
        (
            [
                "raw_data",
            ],
            "RawData",
        ),
        (
            ["val1"],
            "Val1",
        ),
        (["val1", "val2"], "Val1Val2"),
        (["", "val1", "", "val2", ""], "Val1Val2"),
    ],
)
def test_class_name(strs: Sequence[str], expected) -> None:
    assert utils.class_name(*strs) == expected
