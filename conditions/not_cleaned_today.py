from cleaner import START, END
from condition import Condition


class NotCleanedToday(Condition):
    def __init__(self, influx_client):
        self.__influx_client = influx_client

    def is_satisfied(self):
        return self.__influx_client.has_cleaned(START, END)
