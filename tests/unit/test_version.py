# pylint: disable=redefined-outer-name

from typing import Sequence
import datetime

import pytest
from _pytest.fixtures import SubRequest

from i_vis.core import version


@pytest.fixture
def unknown_version() -> version.Unknown:
    return version.Unknown()


class TestUnknown:
    def test_str(self, unknown_version: version.Unknown) -> None:
        assert str(unknown_version) == "Unknown"

    @pytest.mark.parametrize(
        "version1,version2,expected",
        [
            (version.Unknown(), version.Unknown(), False),
            (version.Unknown(), version.Version(), False),
            (version.Version(), version.Unknown(), False),
        ],
    )
    def test_eq(
        self, version1: version.Version, version2: version.Version, expected: bool
    ) -> None:
        assert (version1 == version2) == expected

    @pytest.mark.parametrize(
        "unknown_version1,unknown_version2", [(version.Unknown(), version.Unknown())]
    )
    def test_lt(
        self, unknown_version1: version.Unknown, unknown_version2: version.Unknown
    ) -> None:
        assert not unknown_version1 < unknown_version2

    @pytest.mark.parametrize(
        "unknown_version1,unknown_version2", [(version.Unknown(), version.Unknown())]
    )
    def test_gt(
        self, unknown_version1: version.Unknown, unknown_version2: version.Unknown
    ) -> None:
        assert not unknown_version1 > unknown_version2


def create_date_version(s: str) -> version.Date:
    return version.Date(datetime.date.fromisoformat(s))


@pytest.fixture
def date_version(request: SubRequest) -> version.Date:
    # e.g.: "2020-6-2"
    return create_date_version(request.param)


class TestDate:
    @pytest.mark.parametrize(
        "date_version,expected",
        [
            ("2020-06-02", 2020),
            ("2000-07-03", 2000),
        ],
        indirect=["date_version"],
    )
    def test_year(self, date_version: version.Date, expected: int) -> None:
        assert date_version.year == expected

    @pytest.mark.parametrize(
        "date_version,expected",
        [
            ("2020-06-02", 6),
            ("2000-07-03", 7),
        ],
        indirect=["date_version"],
    )
    def test_month(self, date_version: version.Date, expected: int) -> None:
        assert date_version.month == expected

    @pytest.mark.parametrize(
        "date_version,expected",
        [
            ("2020-06-02", 2),
            ("2000-07-03", 3),
        ],
        indirect=["date_version"],
    )
    def test_day(self, date_version: version.Date, expected: int) -> None:
        assert date_version.day == expected

    @pytest.mark.parametrize(
        "date_version,expected",
        [
            ("2020-06-02", "2020/06/02"),
            ("2000-07-03", "2020/07/03"),
        ],
        indirect=["date_version"],
    )
    def test_str(self, date_version: version.Date, expected: str) -> None:
        assert str(date_version), expected

    @pytest.mark.parametrize(
        "date_version1,date_version2, expected",
        [
            (
                create_date_version("2020-06-02"),
                create_date_version("2020-06-02"),
                True,
            ),
            (
                create_date_version("2020-06-01"),
                create_date_version("2020-06-02"),
                False,
            ),
            (
                create_date_version("2020-07-02"),
                create_date_version("2020-06-02"),
                False,
            ),
            (
                create_date_version("2021-06-02"),
                create_date_version("2020-06-02"),
                False,
            ),
        ],
    )
    def test_eq(
        self, date_version1: version.Date, date_version2: version.Date, expected: bool
    ) -> None:
        assert (date_version1 == date_version2) == expected

    @pytest.mark.parametrize(
        "date_version1,date_version2, expected",
        [
            (
                create_date_version("2020-06-02"),
                create_date_version("2020-06-02"),
                False,
            ),
            (
                create_date_version("2020-06-01"),
                create_date_version("2020-06-02"),
                True,
            ),
            (
                create_date_version("2020-06-02"),
                create_date_version("2020-07-02"),
                True,
            ),
            (
                create_date_version("2020-06-02"),
                create_date_version("2021-06-02"),
                True,
            ),
            (
                create_date_version("2020-06-02"),
                create_date_version("2020-06-01"),
                False,
            ),
            (
                create_date_version("2020-07-02"),
                create_date_version("2020-06-02"),
                False,
            ),
            (
                create_date_version("2021-06-02"),
                create_date_version("2020-06-02"),
                False,
            ),
        ],
    )
    def test_lt(
        self, date_version1: version.Date, date_version2: version.Date, expected: bool
    ) -> None:
        assert (date_version1 < date_version2) == expected

    @pytest.mark.parametrize(
        "date_version, expected",
        [
            ("2020-05-01", datetime.date(year=2020, month=5, day=1)),
            ("2021-06-02", datetime.date(year=2021, month=6, day=2)),
        ],
        indirect=["date_version"],
    )
    def test_to_date(self, date_version: version.Date, expected: datetime.date) -> None:
        assert date_version.to_date() == expected

    @pytest.mark.parametrize(
        "s, expected",
        [
            ("2020_05_01", create_date_version("2020-05-01")),
            ("2021_06_02", create_date_version("2021-06-02")),
        ],
    )
    def test_from_str(self, s: str, expected: version.Date) -> None:
        assert version.Date.from_str(s) == expected


@pytest.fixture
def default_version(request: SubRequest) -> version.Default:
    return version.Default(**request.param)


class TestDefault:
    @pytest.mark.parametrize(
        "default_version,expected",
        [
            (version.Default(major=1), "1"),
            (version.Default(major=1, minor=2, patch=3), "1.2.3"),
            (
                version.Default(
                    major=1, minor=2, patch=3, prefix="test-", suffix="-staging"
                ),
                "test-1.2.3-staging",
            ),
        ],
    )
    def test_str(self, default_version: version.Date, expected: str) -> None:
        assert str(default_version) == expected

    @pytest.mark.parametrize(
        "default_version1,default_version2,expected",
        [
            (version.Default(major=1), version.Default(major=1), True),
            (
                version.Default(major=1, minor=2, patch=3),
                version.Default(major=1, minor=2, patch=3),
                True,
            ),
            (
                version.Default(
                    major=1, minor=2, patch=3, prefix="test-", suffix="-staging"
                ),
                version.Default(
                    major=1, minor=2, patch=3, prefix="test-", suffix="-staging"
                ),
                True,
            ),
            (
                version.Default(major=1, minor=2, patch=3),
                version.Default(major=1, minor=1, patch=3),
                False,
            ),
            (
                version.Default(major=1, minor=2, patch=3),
                version.Default(major=1, minor=2, patch=2),
                False,
            ),
            (
                version.Default(major=1, minor=2, patch=3),
                version.Default(major=2, minor=2, patch=3),
                False,
            ),
            (
                version.Default(major=1, minor=2, patch=3, suffix="-stagging"),
                version.Default(major=1, minor=2, patch=3),
                False,
            ),
        ],
    )
    def test_eq(
        self,
        default_version1: version.Date,
        default_version2: version.Date,
        expected: bool,
    ) -> None:
        assert (default_version1 == default_version2) == expected

    @pytest.mark.parametrize(
        "default_version1,default_version2, expected",
        [
            (
                version.Default(major=1, prefix="testing", suffix="alpha"),
                version.Default(major=1),
                False,
            ),
            (
                version.Default(major=1, minor=0),
                version.Default(major=1, minor=0),
                False,
            ),
            (
                version.Default(major=1, minor=0, patch=1),
                version.Default(major=1, minor=0, patch=1),
                False,
            ),
            (
                version.Default(major=1, minor=0, patch=1),
                version.Default(major=1, minor=1, patch=1),
                True,
            ),
            (
                version.Default(major=1, minor=1, patch=1),
                version.Default(major=1, minor=1, patch=2),
                True,
            ),
            (
                version.Default(major=1, minor=1),
                version.Default(major=1, minor=1, patch=1),
                True,
            ),
        ],
    )
    def test_lt(
        self,
        default_version1: version.Default,
        default_version2: version.Default,
        expected: bool,
    ) -> None:
        assert (default_version1 < default_version2) == expected

    @pytest.mark.parametrize(
        "s,expected",
        [
            ("pre-1.1.2-post", version.Default(1, 1, 2, prefix="pre-", suffix="-post")),
            ("1.1.2", version.Default(1, 1, 2)),
            ("1.1", version.Default(1, 1)),
            ("1", version.Default(1)),
        ],
    )
    def test_from_str(self, s: str, expected: version.Default) -> None:
        assert version.Default.from_str(s) == expected


@pytest.mark.parametrize(
    "s,expected",
    [
        ("1.1.1", version.Default(1, 1, 1)),
        ("1.0.0", version.Default(1, 0, 0)),
        ("1.1", version.Default(1)),
        ("1", version.Default(1)),
        ("2020_01_25", version.Date(datetime.date(year=2020, month=1, day=25))),
        ("4.1a", version.Default(major=1, minor=1, suffix="a")),
    ],
)
def test_from_str(s: str, expected: version.Version) -> None:
    assert version.from_str() == expected


def test_by_xpath() -> None:
    assert False


def test_last_modified() -> None:
    assert False


@pytest.mark.parametrize(
    "dates,expected",
    [
        (
            [
                datetime.date(year=2001, month=1, day=1),
                datetime.date(year=2002, month=1, day=1),
            ],
            datetime.date(year=2002, month=1, day=1),
        ),
        (
            [
                datetime.date(year=2002, month=1, day=1),
            ],
            datetime.date(year=2002, month=1, day=1),
        ),
    ],
)
def test_recent(dates: Sequence[datetime.date], expected: datetime.date) -> None:
    assert version.recent(*dates) == expected
