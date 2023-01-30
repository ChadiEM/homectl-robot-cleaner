from condition import Condition
from conditions.time_bounds import START, END
from influx_client import InfluxClient


class NotCleanedToday(Condition):
    def __init__(self, influx_client: InfluxClient):
        self.__influx_client = influx_client

    def is_satisfied(self) -> bool:
        return not self.__influx_client.has_cleaned(START, END)

    def should_recheck(self) -> bool:
        return False
