from dateutil.rrule import rrule, WEEKLY
from datetime import datetime
import json
test = rrule(WEEKLY, datetime.now(), 2, count=4)

reply = [date.isoformat().replace("'", '"') for date in list(test)]
print(json.dumps(reply))
