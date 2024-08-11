from dateutil.rrule import rrule
from datetime import datetime, date


def dateListRRule(freq: int, date: date, interval: int, nbEpisodes: int, amount: int) -> list[str]:
    rr = rrule(
        freq=freq,
        dtstart=date,
        interval=interval,
        count=nbEpisodes/amount
    )

    return [dt.isoformat() for dt in list(rr)]
