from dateutil.rrule import rrule
from datetime import date

# TODO: Determine what to do when uneven number of episodes


def dateListRRule(freq: int, date: date, interval: int, nbEpisodes: int, amount: int) -> list[str]:
    rr = rrule(
        freq=freq,
        dtstart=date,
        interval=interval,
        count=nbEpisodes/amount
    )

    return [dt.isoformat() for dt in list(rr)]
