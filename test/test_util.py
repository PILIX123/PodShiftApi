from utils.util import dateListRRule
from datetime import datetime


def test_dateListRRule_daily_once_a_day():
    freq = 3
    amount = 1
    nbEpisodes = 10
    startDate = datetime(2024, 5, 5)
    everyX = 1
    expectedDates = [
        datetime(2024, 5, 5),
        datetime(2024, 5, 6),
        datetime(2024, 5, 7),
        datetime(2024, 5, 8),
        datetime(2024, 5, 9),
        datetime(2024, 5, 10),
        datetime(2024, 5, 11),
        datetime(2024, 5, 12),
        datetime(2024, 5, 13),
        datetime(2024, 5, 14),
    ]

    expected = [dt.isoformat() for dt in expectedDates]
    real = dateListRRule(
        freq=freq,
        date=startDate,
        interval=everyX,
        nbEpisodes=nbEpisodes,
        amount=amount
    )
    assert expected == real


def test_dateListRRule_daily_twice_a_day():
    freq = 3
    amount = 2
    nbEpisodes = 10
    startDate = datetime(2024, 5, 5)
    everyX = 1
    expectedDates = [
        datetime(2024, 5, 5),
        datetime(2024, 5, 6),
        datetime(2024, 5, 7),
        datetime(2024, 5, 8),
        datetime(2024, 5, 9),
    ]

    expected = [dt.isoformat() for dt in expectedDates]
    real = dateListRRule(
        freq=freq,
        date=startDate,
        interval=everyX,
        nbEpisodes=nbEpisodes,
        amount=amount
    )
    assert real == expected


def test_dateListRRule_daily_twice_a_day_uneven():
    freq = 3
    amount = 2
    nbEpisodes = 9
    startDate = datetime(2024, 5, 5)
    everyX = 1
    expectedDates = [
        datetime(2024, 5, 5),
        datetime(2024, 5, 6),
        datetime(2024, 5, 7),
        datetime(2024, 5, 8),
        datetime(2024, 5, 9),
    ]

    expected = [dt.isoformat() for dt in expectedDates]
    real = dateListRRule(
        freq=freq,
        date=startDate,
        interval=everyX,
        nbEpisodes=nbEpisodes,
        amount=amount
    )
    assert real == expected


def test_dateListRRule_weekly_once_a_week():
    freq = 2
    amount = 1
    nbEpisodes = 10
    startDate = datetime(2024, 5, 5)
    everyX = 1
    expectedDates = [
        datetime(2024, 5, 5),
        datetime(2024, 5, 12),
        datetime(2024, 5, 19),
        datetime(2024, 5, 26),
        datetime(2024, 6, 2),
        datetime(2024, 6, 9),
        datetime(2024, 6, 16),
        datetime(2024, 6, 23),
        datetime(2024, 6, 30),
        datetime(2024, 7, 7),
    ]

    expected = [dt.isoformat() for dt in expectedDates]
    real = dateListRRule(
        freq=freq,
        date=startDate,
        interval=everyX,
        nbEpisodes=nbEpisodes,
        amount=amount
    )
    assert real == expected


def test_dateListRRule_weekly_twice_a_week():
    freq = 2
    amount = 2
    nbEpisodes = 10
    startDate = datetime(2024, 5, 5)
    everyX = 1
    expectedDates = [
        datetime(2024, 5, 5),
        datetime(2024, 5, 12),
        datetime(2024, 5, 19),
        datetime(2024, 5, 26),
        datetime(2024, 6, 2)
    ]

    expected = [dt.isoformat() for dt in expectedDates]
    real = dateListRRule(
        freq=freq,
        date=startDate,
        interval=everyX,
        nbEpisodes=nbEpisodes,
        amount=amount
    )
    assert real == expected
    assert 1 == 1
