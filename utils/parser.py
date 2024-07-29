from collections import Counter
from dateutil.rrule import rrule, WEEKLY, DAILY, YEARLY, MONTHLY
from dateutil import parser


def create_rrule_from_dates(iso_dates):
    # Parse the ISO formatted dates into datetime objects
    dates = [parser.isoparse(date) for date in iso_dates]

    # Analyze the pattern
    frequency, interval = analyze_pattern(dates)

    # Create the rrule object
    rr = rrule(
        freq=frequency,
        dtstart=dates[0],
        interval=interval,
        until=dates[-1]  # Optionally, specify the end date
    )

    return rr


# Example usage
iso_dates = [
    "2024-07-28T10:00:00Z",
    "2024-08-28T10:00:00Z",
    "2024-09-28T10:00:00Z"
]


def analyze_pattern(dates):
    if len(dates) < 2:
        raise ValueError(
            "At least two dates are required to determine the pattern.")

    # Calculate the differences between consecutive dates
    deltas = [dates[i] - dates[i - 1] for i in range(1, len(dates))]

    # Identify the most common delta (this will be our interval)
    most_common_delta = Counter(deltas).most_common(1)[0][0]

    # Determine the frequency
    if most_common_delta.days % 365 == 0:
        frequency = YEARLY
        interval = most_common_delta.days // 365
    elif most_common_delta.days % 30 == 0:
        frequency = MONTHLY
        interval = most_common_delta.days // 30
    elif most_common_delta.days % 7 == 0:
        frequency = WEEKLY
        interval = most_common_delta.days // 7
    elif most_common_delta.days == 1:
        frequency = DAILY
        interval = 1
    else:
        raise ValueError("Unsupported frequency detected.")

    return frequency, interval
