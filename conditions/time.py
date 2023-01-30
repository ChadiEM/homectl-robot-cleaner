from datetime import datetime

from condition import Condition
from conditions.time_bounds import START, END


class Time(Condition):
    def is_satisfied(self) -> bool:
        return START <= datetime.now() <= END

    def should_recheck(self) -> bool:
        return False
