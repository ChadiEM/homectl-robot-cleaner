from datetime import datetime

from condition import Condition
from conditions.time_bounds import START, END


class Time(Condition):
    def is_satisfied(self):
        return START <= datetime.now() <= END
