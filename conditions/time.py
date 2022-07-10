from datetime import datetime

from cleaner import START, END
from condition import Condition


class Time(Condition):
    def is_satisfied(self):
        return START <= datetime.now() <= END
