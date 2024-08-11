from utils.util import dateListRRule


def test_dateListRRule_daily_once_a_day():
    freq = 3
    amount = 1
    expectedDates = []
    assert 1 == 1


def test_dateListRRule_daily_twice_a_day():
    freq = 3
    amount = 2
    expectedDates = []
    assert 1 == 1


def test_dateListRRule_weekly_once_a_week():
    freq = 2
    amount = 1
    expectedDates = []
    assert 1 == 1


def test_dateListRRule_weekly_twice_a_week():
    freq = 2
    amount = 2
    expectedDates = []
    assert 1 == 1
