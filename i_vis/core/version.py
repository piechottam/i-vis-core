from typing import Any, Dict, MutableMapping, Optional, Sequence
import datetime
import re

from lxml import etree
import requests


MAX_VERSION_LENGTH = 20
DATE_FORMAT = "%Y_%m_%d"


def format_date(date: datetime.date) -> str:
    return date.strftime(DATE_FORMAT)


class UnknownVersionError(Exception):
    pass


class Version:
    """Base class"""

    def __str__(self) -> str:
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        raise NotImplementedError

    def __lt__(self, other) -> bool:
        raise NotImplementedError

    def __hash__(self) -> int:
        raise NotImplementedError

    @property
    def is_known(self):
        return True


class Unknown(Version):
    """Unknown version"""

    def __str__(self) -> str:
        return "Unknown"

    def __eq__(self, other) -> bool:
        if isinstance(other, Version):
            return False
        return NotImplemented

    def __lt__(self, other) -> bool:
        if isinstance(other, Unknown):
            return False
        return NotImplemented

    def __hash__(self):
        return NotImplemented

    @property
    def is_known(self) -> bool:
        return False


class Date(Version):
    """Version based on a date"""

    def __init__(self, date: datetime.date) -> None:
        self._date = date

    @property
    def year(self) -> int:
        return self._date.year

    @property
    def month(self) -> int:
        return self._date.month

    @property
    def day(self) -> int:
        return self._date.day

    def __str__(self) -> str:
        return format_date(self._date)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Date):
            return str(self) == str(other)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Date):
            return lessthan(self, other, ["year", "month", "day"])
        return NotImplemented

    def __hash__(self):
        return hash(self._date)

    def date(self) -> datetime.date:
        return datetime.date(
            year=self._date.year, month=self._date.month, day=self._date.day
        )

    @staticmethod
    def fromurl(**kwargs) -> Optional["Date"]:
        modified = last_modified(**kwargs)
        if modified:
            return Date(modified)
        return None

    @staticmethod
    def from_db(s) -> "Date":
        return Date(datetime.datetime.strptime(s, DATE_FORMAT))


class Nightly(Date):
    def __init__(self) -> None:
        super().__init__(datetime.date.today())


DEAFULT_PATTERN = re.compile(
    r"(?P<prefix>.*[^\d+])?(?P<major>\d+)(\.(?P<minor>\d+))?(\.(?P<patch>\d+))?(?P<suffix>.*)"
)


class Default(Version):
    """major.minor.patch"""

    def __init__(
        self,
        major: int,
        minor: int = None,
        patch: int = None,
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        self._major = major
        self._minor = minor
        self._patch = patch
        self._prefix = prefix
        self._suffix = suffix

    @property
    def major(self) -> int:
        return self._major

    @property
    def minor(self) -> Optional[int]:
        return self._minor

    @property
    def patch(self) -> Optional[int]:
        return self._patch

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def suffix(self) -> str:
        return self._suffix

    def __str__(self) -> str:
        s = [str(v) for v in [self._major, self._minor, self._patch] if v is not None]
        return f'{self._prefix}{".".join(s)}{self._suffix}'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Default):
            return str(self) == str(other)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Default):
            attrs = [
                attr for attr in ("major", "minor", "patch") if getattr(self, attr)
            ]
            return lessthan(self, other, attrs)
        return NotImplemented

    def __hash__(self):
        return hash(tuple(v for v in (self._major, self._minor, self._patch) if v))

    @staticmethod
    def from_db(s: str) -> "Default":
        match = re.match(DEAFULT_PATTERN, s)
        if match is not None:
            matched: MutableMapping[str, Any] = {}
            for key, value in match.groupdict().items():
                if value is None:
                    continue
                if key in ("major", "minor", "patch"):
                    matched[key] = int(value)
                else:
                    matched[key] = value
            return Default(**matched)

        raise ValueError(f"Version could not be parsed from: {s}")


def lessthan(self, other: Version, attrs: Sequence[str]) -> bool:
    for attr in attrs:
        if getattr(self, attr) < getattr(other, attr):
            return True
        if getattr(self, attr) > getattr(other, attr):
            return False
    return False


def by_xpath(url: str, xpath: str) -> str:
    """Retrieve version string from url using xpath"""
    r = requests.get(url, timeout=100)
    if r.status_code != 200:
        raise ValueError(f"Status code ({r.status_code}) != 200")
    parser = etree.HTMLParser()
    tree = etree.fromstring(r.text, parser=parser)
    return str(tree.xpath(xpath).pop().text)


def last_modified(
    url: str,
    request_args: Optional[Dict] = None,
    date_format: str = "%a, %d %b %Y %H:%M:%S GMT",
) -> Optional[datetime.date]:
    """Retrieve last modified from header of url"""
    if not request_args:
        request_args = {}
    r = requests.head(url, **request_args)
    key = "Last-Modified"
    if key not in r.headers:
        return None
    return datetime.datetime.strptime(r.headers[key], date_format)


def recent(*dates: datetime.date) -> datetime.date:
    """Determine most recent date from list of dates"""
    return max(*dates)
