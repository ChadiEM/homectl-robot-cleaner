from cleaner import clock
from cleaner.condition import Condition
from cleaner.conditions.time_bounds import START, END


class Time(Condition):
    def __init__(self) -> None:
        super().__init__(False)

    def is_satisfied(self) -> bool:
        return START <= clock.time() <= END
