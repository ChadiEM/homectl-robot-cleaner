from condition import Condition
from conditions.time_bounds import START, END


class NotCleanedToday(Condition):
    def __init__(self, influx_client):
        self.__influx_client = influx_client

    def is_satisfied(self):
        return not self.__influx_client.has_cleaned(START, END)
