# pylint: disable=redefined-outer-name

import os

import pytest

from i_vis.core import file_utils


@pytest.mark.parametrize(
    "url,expected",
    [
        ("http://www.test.com/test_path/file", "file"),
        ("http://www.test.com/TestFile", "test_file"),
    ],
)
def test_url2fname(url: str, expected: str) -> None:
    assert file_utils.url2fname(url) == expected


@pytest.mark.parametrize(
    "fname,pre,tag,expected",
    [
        ("/path/file", "prefix", "", "/path/prefix-file"),
        ("/path/file", "prefix", "test-tag", "/path/prefix-test-tag-file"),
    ],
)
def test_prefix_fname(fname: str, pre: str, tag: str, expected: str) -> None:
    assert file_utils.prefix_fname(fname, pre, tag) == expected


@pytest.mark.parametrize(
    "fname,new_suffix,old_suffix,expected",
    [
        ("/path/file.txt", ".tsv", "", "/path/file.tsv"),
        ("/path/file.txt.zip", "", ".zip", "/path/file.txt"),
        ("/path/file.txt.zip", ".txt", ".txt.zip", "/path/file.txt"),
    ],
)
def test_change_suffix(
    fname: str, new_suffix: str, old_suffix: str, expected: str
) -> None:
    assert (
        file_utils.change_suffix(
            fname=fname, new_suffix=new_suffix, old_suffix=old_suffix
        )
        == expected
    )


@pytest.fixture
def mini_file() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "static", "10-lines.txt")


def test_md5(mini_file: str) -> None:
    assert file_utils.md5(mini_file) == "fc69a359565f35bf130a127ae2ebf2da"


def test_size(mini_file: str) -> None:
    assert file_utils.size(mini_file) == 20


def test_lines(mini_file: str) -> None:
    assert file_utils.lines(mini_file) == 10


@pytest.mark.parametrize(
    "s,expected",
    [
        ("path/test file", "path_test_file"),
        ("    $+#path/test file", "path_test_file"),
        (" _test", "_test"),
    ],
)
def test_clean(s: str, expected: str) -> None:
    assert file_utils.clean(s) == expected
