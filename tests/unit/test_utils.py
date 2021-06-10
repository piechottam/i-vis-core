import pytest

from i_vis.core import utils


@pytest.mark.parametrize("targets,expected", [("test", True)])
def test_is_safe_url(targets, expected):
    assert utils.is_safe_url(targets) == expected


class TestEnumMixin:
    pass


class TestEnumUtils:
    pass


def test_datetime_format():
    pass


def test_datatable_columns():
    pass


def test_datatable_render_link():
    assert False


def test_render_link():
    assert (
        utils.render_link("url_value", "label_value")
        == '<a href="url_value">label_value</a>'
    )


def test_register_datatable_query():
    assert False


def test_register_autocomplete():
    assert False
