from cleaner.condition import Condition
from cleaner.influx_client import InfluxClient


class NotCleanedToday(Condition):
    def __init__(self, influx_client: InfluxClient):
        super().__init__(False)
        self.__influx_client = influx_client

    def is_satisfied(self) -> bool:
        return not self.__influx_client.has_cleaned_today()
