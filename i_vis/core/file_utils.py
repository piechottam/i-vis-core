from datetime import datetime
from urllib.parse import urlparse
import hashlib
import logging
import os
import pathlib
import re

from inflection import underscore


def is_local(url: str) -> bool:
    o = urlparse(url)
    return o.scheme.lower() == "file"


def url2fname(url: str) -> str:
    """Convert URL to fname"""
    res = urlparse(url)
    basename = os.path.basename(res.path)
    return underscore(basename)


def prefix_fname(fname: str, pre: str, tag: str = "") -> str:
    """Prefix fname with pre and and optional tag"""
    d = os.path.dirname(fname)
    if d:
        d = d + "/"
    f = os.path.basename(fname)
    if tag:
        pre = f"{pre}-{tag}"
    pre = f"{pre}-"
    return f"{d}{pre}{f}"


def change_suffix(fname: str, new_suffix: str, old_suffix: str = "") -> str:
    if not old_suffix:
        old_suffix = os.path.splitext(fname)[1]
    return str(re.sub(old_suffix + "$", new_suffix, fname))


def md5(fname: str) -> str:
    """MD5 hash value for fname"""
    h = hashlib.md5()
    with open(fname, "rb") as f:
        while True:
            data = f.read(1024 * 64)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def size(fname: str) -> int:
    """Size of fname in Bytes"""
    return os.stat(fname).st_size


def lines(fname: str) -> int:
    return sum(1 for _ in open(fname, "rb"))


def clean(s: str) -> str:
    s = re.sub("[ /]+", "_", s)
    s = re.sub("[^0-9a-zA-Z_.]", "", s)
    return s


def create_dir(dname: str) -> None:
    if not os.path.exists(dname):
        pathlib.Path(dname).mkdir(parents=True)
        logging.debug("Created directory: %s", dname)


def read_query(fname: str) -> str:
    with open(fname, "r") as f:
        s = f.read()
        return re.sub(r"\s+(?=<)", "", s)


def modified(fname: str) -> datetime:
    mtime = os.stat(fname).st_mtime
    return datetime.fromtimestamp(mtime)
