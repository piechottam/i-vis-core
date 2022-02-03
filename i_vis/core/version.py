"""Version specific methods.

Each data source is required to have version information.

The following version types can be represented by implementing :class:`Version` abstract class:

* semantic versioning (e.g.: [pre-]x.y.z[-post]
* date based (e.g.: nightly release -> YYMMDD))
* unknown version by: :class:`Unknown`

Version information can be compared with:
"<", ">", "==", ">=", and "<=".

Examples:
    >>> v = Default(major=1, minor=0)
    >>> w = Default(major=1, minor=1)
    >>> v < w
    True
"""

from typing import Any, Dict, MutableMapping, Optional, Sequence
import datetime
import re

import requests
from lxml import etree

from .utils import StatusCode200Error


#: Maximum allowed version length.
MAX_VERSION_LENGTH = 20
#: Default date format to store version info
DATE_FORMAT = "%Y_%m_%d"


class UnknownVersionError(Exception):
    pass


class ParseError(Exception):
    pass


class Version:
    """Base class for version information."""

    def __str__(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError

    def __lt__(self, other: Any) -> bool:
        raise NotImplementedError

    def __hash__(self) -> int:
        raise NotImplementedError

    @property
    def is_known(self) -> bool:
        return True


class Unknown(Version):
    """Unknown version."""

    def __str__(self) -> str:
        return "Unknown"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Version):
            return False
        return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Unknown):
            return False
        return NotImplemented

    def __hash__(self) -> int:
        return 0

    @property
    def is_known(self) -> bool:
        return False


class Date(Version):
    """Version based on a date."""

    def __init__(self, date: datetime.date) -> None:
        self.date = date

    @property
    def year(self) -> int:
        return self.date.year

    @property
    def month(self) -> int:
        return self.date.month

    @property
    def day(self) -> int:
        return self.date.day

    def __str__(self) -> str:
        return self.date.strftime(DATE_FORMAT)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Date):
            return str(self) == str(other)
        return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Date):
            return less_than(self, other, ["year", "month", "day"])
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.date)

    def to_date(self) -> datetime.date:
        return datetime.date(
            year=self.date.year, month=self.date.month, day=self.date.day
        )

    # FIXME raise exceptions
    @staticmethod
    def from_url(url: str, **kwargs: Any) -> "Date":
        """Create version from date info for an url.

        Args:
            url: Url to check for modification.
            **kwargs: see :method:`last_modified` for details.

        Returns:
            :class:`Date` or ``None``, if no date information could be retrieved.
        """

        modified = last_modified(url, **kwargs)
        if not modified:
            raise ValueError(f"Could not retrieve last modified from '{url}'.")

        return Date(modified)

    @staticmethod
    def from_xpath(url: str, xpath: str, format_: str) -> "Date":
        s = by_xpath(url, xpath)
        # connection error
        # parse error
        date = datetime.datetime.strptime(s, format_)
        # format error
        return Date(date)

    @staticmethod
    def from_str(s: str) -> "Date":
        return Date(datetime.datetime.strptime(s, DATE_FORMAT))


class Nightly(Date):
    def __init__(self) -> None:
        super().__init__(datetime.date.today())


DEFAULT_PATTERN = re.compile(
    r"(?P<prefix>.*[^\d+])?(?P<major>\d+)(\.(?P<minor>\d+))?(\.(?P<patch>\d+))?(?P<suffix>.*)"
)


class Default(Version):
    """Semantic versioning.

    Capture format: [pre-]major.minor.patch[-suffix]
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        major: int,
        minor: Optional[int] = None,
        patch: Optional[int] = None,
        prefix: str = "",
        suffix: str = "",
    ) -> None:
        # TODO check types

        self.major = major
        self.minor = minor
        self.patch = patch
        self.prefix = prefix
        self.suffix = suffix

    def __str__(self) -> str:
        s = [str(v) for v in [self.major, self.minor, self.patch] if v is not None]
        return f'{self.prefix}{".".join(s)}{self.suffix}'

    def __repr__(self) -> str:
        values = tuple(
            f"{v}={getattr(self, v)}"
            for v in ("major", "minor", "patch", "prefix", "suffix")
            if v is not None
        )
        return "Default(" + ", ".join(values) + ")"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Default):
            return str(self) == str(other)
        return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Default):
            return less_than(self, other, ("major", "minor", "patch"))
        return NotImplemented

    def __hash__(self) -> int:
        return hash(tuple(v for v in (self.major, self.minor, self.patch) if v))

    @staticmethod
    def from_str(s: str) -> "Default":
        match = re.match(DEFAULT_PATTERN, s)
        if match is None:
            raise ValueError(f"Version could not be parsed from: {s}")

        matched: MutableMapping[str, Any] = {}
        for key, value in match.groupdict().items():
            if value is None:
                continue
            if key in ("major", "minor", "patch"):
                matched[key] = int(value)
            else:
                matched[key] = value
        return Default(**matched)


# FIMXE DateVerion parse as DefaultVersion
# def from_str(s: str) -> "Version":
#    for obj in (Default, Date):
#        try:
#            return obj.from_str(s)
#        except ValueError:
#            continue
#
#    raise ParseError(s)


def less_than(self: Version, other: Version, attrs: Sequence[str]) -> bool:
    """Compare versions based on attributes.

    ``self`` and ``other`` be the same type.

    Args:
        self: A :class:`Version` instance to compare.
        other: An other :class:`Version` instance to compare against.
        attrs: Attributes to compare.

    Returns:
        True, if ``self`` is older than ``other``. False, otherwise.
    """

    for attr in attrs:
        attr1 = getattr(self, attr, None)
        attr2 = getattr(other, attr, None)

        if attr1 is not None:
            if attr2 is None:
                return False
            if attr1 < attr2:
                return True
            if attr1 > attr2:
                return False
        else:
            if attr2 is not None:
                return True
    return False


def by_xpath(url: str, xpath: str, **kwargs: Any) -> str:
    """Retrieve version string from url using xpath.

    Args:
        url: Url to retrieve version string from.
        xpath: XPATH of version string.
        kwargs: Arguments forwarded to :module:`requests`.

    Returns:
        Version string info from ``url`` identified by ``xpath``.

    Raises:
        ValueError if cannot connect to ``url``.
    """

    r = requests.get(url, timeout=100, **kwargs)
    if r.status_code != 200:
        raise StatusCode200Error(reponse=r)

    parser = etree.HTMLParser()
    tree = etree.fromstring(r.text, parser=parser)  # type: ignore
    return str(tree.xpath(xpath).pop().text)  # type: ignore


def last_modified(
    url: str,
    request_args: Optional[Dict[str, Any]] = None,
    date_format: str = "%a, %d %b %Y %H:%M:%S GMT",
) -> Optional[datetime.date]:
    """Retrieve last modified from header of url.

    Args:
        url: Url to check header info.
        request_args: (Optional) Arguments forwarded to :module:`requests`.
        date_format: Expected data format in header info. Default: "%a, %d %b %Y %H:%M:%S GMT".

    Returns:
        Last modification datetime for ``url`` or None.
    """

    if not request_args:
        request_args = {}
    r = requests.head(url, timeout=100, **request_args)
    if r.status_code != 200:
        return None

    key = "Last-Modified"
    if key not in r.headers:
        return None
    return datetime.datetime.strptime(r.headers[key], date_format)


def recent(*dates: datetime.date) -> datetime.date:
    """Determine most recent date from list of dates.

    Args:
        *dates: Sequence of dates to check.

    Returns:
        Most recent date from ``*dates``.
    """

    return max(*dates)
