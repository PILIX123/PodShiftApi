from dateutil.rrule import rrule, WEEKLY
from datetime import datetime
import json
from uuid import uuid1
test = rrule(WEEKLY, datetime.now(), 2, count=4)

reply = [date.isoformat() for date in list(test)]
print(json.dumps(reply))
print(uuid1())
