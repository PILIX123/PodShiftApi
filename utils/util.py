from dateutil.rrule import rrule
from datetime import date
from math import ceil
# TODO: Determine what to do when uneven number of episodes


def dateListRRule(freq: int, date: date, interval: int, nbEpisodes: int, amount: int) -> list[str]:
    rr = rrule(
        freq=freq,
        dtstart=date,
        interval=interval,
        count=ceil(nbEpisodes/amount)
    )

    return [dt.isoformat() for dt in list(rr)]
