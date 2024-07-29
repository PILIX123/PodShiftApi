from dateutil.rrule import rrule, WEEKLY
from datetime import datetime
test = rrule(WEEKLY, datetime.now(), 2, count=4)
print(list(test))
