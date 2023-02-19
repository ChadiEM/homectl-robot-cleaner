import abc
import datetime
import os
from datetime import time

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client import write_api

from cleaner import clock


class InfluxClient(abc.ABC):
    @abc.abstractmethod
    def has_cleaned(self, start: time, end: time) -> bool:
        pass

    @abc.abstractmethod
    def mark_cleaned(self) -> None:
        pass


class InfluxAPIClient(InfluxClient):
    def __init__(self):
        self.__client = InfluxDBClient(url=os.environ.get('INFLUX_ENDPOINT'),
                                       token=os.environ.get('INFLUX_TOKEN'),
                                       org=os.environ.get('INFLUX_ORG'))

        self.__bucket = os.environ.get('INFLUX_BUCKET')

        self.__query_api = self.__client.query_api()
        self.__write_api = self.__client.write_api(write_options=write_api.SYNCHRONOUS)

    def has_cleaned(self, start: time, end: time):
        start_ts = int(datetime.datetime.combine(datetime.date.today(), start).timestamp())
        stop_ts = int(datetime.datetime.combine(datetime.date.today(), end).timestamp())

        result = self.__query_api.query(f"""from(bucket:"{self.__bucket}")
        |> range(start: {start_ts}, stop: {stop_ts})
        |> filter(fn:(r) => r._measurement == "home_control" and r._field == "robot-clean")""")

        return len(result) > 0

    def mark_cleaned(self):
        self.__write_api.write(bucket=self.__bucket, record=(Point('home_control').field('robot-clean', True).time(
            int(datetime.datetime.combine(datetime.date.today(), clock.time()).timestamp()),
            write_precision=WritePrecision.S)))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__write_api.close()
        self.__client.close()
