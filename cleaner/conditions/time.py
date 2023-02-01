import datetime

from cleaner.condition import Condition
from cleaner.conditions.time_bounds import START, END


class Time(Condition):
    def __init__(self):
        super().__init__(False)

    def is_satisfied(self) -> bool:
        return START <= self.now() <= END

    @staticmethod
    def now() -> datetime.time:
        return datetime.datetime.now().time()
