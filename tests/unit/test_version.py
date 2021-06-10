# pylint: disable=redefined-outer-name

import datetime

import pytest

from i_vis.core import version


@pytest.mark.parametrize(
    "date,expected",
    [
        (datetime.date(year=2002, month=1, day=1), "2002_01_01"),
        (datetime.date(year=2002, month=1, day=30), "2002_01_30"),
    ],
)
def test_format_data(date: datetime.date, expected: str):
    assert version.format_date(date) == expected


@pytest.fixture
def unknown_version():
    return version.Unknown()


class TestUnknown:
    def test_str(self, unknown_version):
        assert str(unknown_version) == "Unknown"

    @pytest.mark.parametrize(
        "version1,version2,expected",
        [
            (version.Unknown(), version.Unknown(), False),
            (version.Unknown(), version.Version(), False),
            (version.Version(), version.Unknown(), False),
        ],
    )
    def test_eq(self, version1, version2, expected):
        assert (version1 == version2) == expected

    @pytest.mark.parametrize(
        "unknown_version1,unknown_version2", [(version.Unknown(), version.Unknown())]
    )
    def test_lt(self, unknown_version1, unknown_version2):
        assert not unknown_version1 < unknown_version2

    @pytest.mark.parametrize(
        "unknown_version1,unknown_version2", [(version.Unknown(), version.Unknown())]
    )
    def test_gt(self, unknown_version1, unknown_version2):
        assert not unknown_version1 > unknown_version2


def create_date_version(s: str):
    return version.Date(datetime.date.fromisoformat(s))


@pytest.fixture
def date_version(request):
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
    def test_year(self, date_version: version.Date, expected: int):
        assert date_version.year == expected

    @pytest.mark.parametrize(
        "date_version,expected",
        [
            ("2020-06-02", 6),
            ("2000-07-03", 7),
        ],
        indirect=["date_version"],
    )
    def test_month(self, date_version: version.Date, expected: int):
        assert date_version.month == expected

    @pytest.mark.parametrize(
        "date_version,expected",
        [
            ("2020-06-02", 2),
            ("2000-07-03", 3),
        ],
        indirect=["date_version"],
    )
    def test_day(self, date_version: version.Date, expected: int):
        assert date_version.day == expected

    @pytest.mark.parametrize(
        "date_version,expected",
        [
            ("2020-06-02", "2020/06/02"),
            ("2000-07-03", "2020/07/03"),
        ],
        indirect=["date_version"],
    )
    def test_str(self, date_version: version.Date, expected: str):
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
    def test_eq(self, date_version1, date_version2, expected: bool):
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
    ):
        assert (date_version1 < date_version2) == expected

    @pytest.mark.parametrize(
        "date_version, expected",
        [
            ("2020-05-01", datetime.date(year=2020, month=5, day=1)),
            ("2021-06-02", datetime.date(year=2021, month=6, day=2)),
        ],
        indirect=["date_version"],
    )
    def test_date(self, date_version: version.Date, expected: datetime.date):
        assert date_version.date() == expected

    def test_fromurl(self):
        assert False

    @pytest.mark.parametrize(
        "s, expected",
        [
            ("2020_05_01", create_date_version("2020-05-01")),
            ("2021_06_02", create_date_version("2021-06-02")),
        ],
    )
    def test_from_db(self, s: str, expected: version.Date):
        assert version.Date.from_db(s) == expected


class TestNightly:
    pass


@pytest.fixture
def default_version(request):
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
    def test_str(self, default_version: version.Date, expected: str):
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
        ],
    )
    def test_eq(
        self,
        default_version1: version.Date,
        default_version2: version.Date,
        expected: bool,
    ):
        assert (default_version1 == default_version2) == expected

    def test_lt(self):
        assert False

    def from_db(self):
        assert False


def test_xpath():
    assert False


def test_last_modified():
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
def test_recent(dates, expected):
    assert version.recent(dates) == expected
