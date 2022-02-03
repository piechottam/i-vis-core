"""Utils for files.
"""
import datetime
import hashlib
import logging
import os
import pathlib
import re
from typing import Optional
from urllib.parse import urlparse

from inflection import underscore


def url2fname(url: str) -> str:
    """Convert URL to fname"""
    res = urlparse(url)
    basename = os.path.basename(res.path)
    return underscore(basename)


def prefix_fname(fname: str, pre: str, tag: Optional[str] = None) -> str:
    """Prefix filename and add optional tag.

    Args:
        fname: Filename to process.
        pre: Prefix to add to filename.
        tag: (Optional). Tag to add to filename. Default = None.

    Returns:
        Prefixed and optionally tagged filename.

    Examples:
        >>> prefix_fname("file.txt", "backup")
        "backup-file.txt"

        >>> prefix_fname("/dir/file.txt", "backup", "old")
        "/dir/backup-old-file.txt"
    """
    dname = os.path.dirname(fname)
    if dname:
        dname = dname + "/"
    fname = os.path.basename(fname).lstrip("_")
    if tag:
        pre = f"{pre}-{tag}"
    pre = f"{pre}-"
    return f"{dname}{pre}{fname}"


def change_suffix(fname: str, new_suffix: str, old_suffix: Optional[str] = None) -> str:
    """Change suffix of filename.

    Changes suffix of a filename. If no old suffix is provided, the part that is replaced is guessed.

    Args:
        fname: Filename to process.
        new_suffix: Replace old suffix with this.
        old_suffix: (Optional) Old suffix of filename - must be part of filename. Default = None.

    Returns:
        Filename with replaced suffix.

    Examples:
        >>> change_suffix("test.txt.gz", "")
        "test.txt"
        >>> change_suffix("test.sorted.txt.gz", ".txt", ".sorted.txt.gz")
        "test.txt"
    """
    if not old_suffix:
        old_suffix = os.path.splitext(fname)[1]
    return str(re.sub(old_suffix + "$", new_suffix, fname))


def md5(fname: str) -> str:
    """MD5 hash value for a file.

    Args:
        fname: File to calculate MD5.

    Returns:
        MD5 hash for filename.
    """
    md5h = hashlib.md5()
    with open(fname, "rb") as file:
        while True:
            data = file.read(1024 * 64)
            if not data:
                break
            md5h.update(data)
    return md5h.hexdigest()


def size(fname: str) -> int:
    """Size of file in Bytes.

    Args:
        fname: Filename to determine the size.

    Returns:
        File size of filename in Bytes.
    """
    return os.stat(fname).st_size


def lines(fname: str) -> int:
    """Lines of file.

    Args:
        fname: Filename to determine line count.

    Returns:
        Line count of filename.
    """

    with open(fname, "rb") as file:
        return sum(1 for _ in file)


def clean_fname(s: str) -> str:
    """

    Args:
        s:

    Returns:

    """
    s = re.sub("^ +", "", s)
    s = re.sub("[ /]+", "_", s)
    s = re.sub("[^0-9a-zA-Z_.]+", "", s)
    return s


def create_dir(dname: str) -> None:
    """Create directory.

    If directory does not exist, create it and write a log message.

    Args:
        dname: Directory to create.
    """
    if not os.path.exists(dname):
        pathlib.Path(dname).mkdir(parents=True)
        logging.debug("Created directory: %s", dname)


def read_query(fname: str) -> str:
    """Read a query from file.

    Read query and remove all white space between tags.

    Args:
        fname: Filename tor read.

    Returns:
        Read query.
    """
    with open(fname, "r") as file:
        s = file.read()
        return re.sub(r"\s+(?=<)", "", s)


def modified(fname: str) -> float:
    """Get modified time.

    Args:
        fname: Filename to get modified time for.

    Returns:
        Modified time of filename.
    """
    return os.stat(fname).st_mtime


def modified_datetime(fname: str) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(modified(fname))


def path_size(path: str) -> int:
    for root, dirs, files in os.walk(path):
        return sum(os.path.getsize(os.path.join(root, file)) for file in files)


def file_count(path: str) -> int:
    for root, dirs, files in os.walk(path):
        return len(files)


def latest_modified_date(path: str) -> int:
    for root, dirs, files in os.walk(path):
        latest_ = max(modified(os.path.join(root, file)) for file in files)
        return datetime.date.fromtimestamp(latest_)

def path_md5(path: str) -> str:
    """MD5 hash value for a file.

    Args:
        fname: File to calculate MD5.

    Returns:
        MD5 hash for filename.
    """

    md5h = hashlib.md5()
    for root, dirs, fnames in os.walk(path):
        for fname in fnames:
            with open(os.path.join(path, fname), "rb") as file:
                while True:
                    data = file.read(1024 * 64)
                    if not data:
                        break
                    md5h.update(data)
    return md5h.hexdigest()
