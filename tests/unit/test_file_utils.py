import pytest

from i_vis.core import file_utils


@pytest.mark.parametrize(
    "url,expected",
    [
        (
            "http://www.test.com/test_path/file",
            "file",
        ),
        ("http://www.test.com/TestFile", "test_file"),
    ],
)
def test_url2fname(url: str, expected: str):
    assert file_utils.url2fname(url) == expected


@pytest.mark.parametrize(
    "fname,pre,tag,expected",
    [
        ("/path/file", "prefix", "", "/path/prefix-file"),
        ("/path/file", "prefix", "test-tag", "/path/prefix-test-tag-file"),
    ],
)
def test_prefix_fname(fname: str, pre: str, tag: str, expected: str):
    assert file_utils.prefix_fname(fname, pre, tag) == expected


@pytest.mark.parametrize(
    "fname,new_suffix,old_suffix,expected",
    [
        ("/path/file.txt", ".tsv", "", "/path/file.tsv"),
        ("/path/file.txt.zip", "", ".zip", "/path/file.txt"),
    ],
)
def test_change_suffix(fname: str, new_suffix: str, old_suffix: str, expected: str):
    assert (
        file_utils.change_suffix(
            fname=fname, new_suffix=new_suffix, old_suffix=old_suffix
        )
        == expected
    )


def test_md5():
    assert False


def test_size():
    assert False


def test_lines():
    assert False


@pytest.mark.parametrize(
    "s,expected",
    [
        ("path/test file", "path_test_file"),
    ],
)
def test_clean(s: str, expected: str):
    assert file_utils.clean(s) == expected


def test_create_dir():
    assert False


def test_read_query():
    assert False


def test_modified():
    assert False
