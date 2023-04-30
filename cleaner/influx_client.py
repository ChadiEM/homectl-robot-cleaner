import abc
import datetime
import os

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client import write_api

from cleaner import clock


class InfluxClient(abc.ABC):
    @abc.abstractmethod
    def has_cleaned_today(self) -> bool:
        pass

    @abc.abstractmethod
    def mark_cleaned_today(self) -> None:
        pass


class InfluxAPIClient(InfluxClient):
    def __init__(self):
        self.__client = InfluxDBClient(url=os.environ.get('INFLUX_ENDPOINT'),
                                       token=os.environ.get('INFLUX_TOKEN'),
                                       org=os.environ.get('INFLUX_ORG'))

        self.__bucket = os.environ.get('INFLUX_BUCKET')

        self.__query_api = self.__client.query_api()
        self.__write_api = self.__client.write_api(write_options=write_api.SYNCHRONOUS)

    def has_cleaned_today(self):
        today = datetime.date.today()
        start_ts = int(datetime.datetime.combine(today, datetime.datetime.min.time()).timestamp())
        stop_ts = int(
            datetime.datetime.combine(today + datetime.timedelta(days=1), datetime.datetime.min.time()).timestamp())

        result = self.__query_api.query(f"""from(bucket:"{self.__bucket}")
        |> range(start: {start_ts}, stop: {stop_ts})
        |> filter(fn:(r) => r._measurement == "home_control" and r._field == "robot-clean")""")

        return len(result) > 0

    def mark_cleaned_today(self):
        self.__write_api.write(bucket=self.__bucket, record=(Point('home_control').field('robot-clean', True).time(
            int(datetime.datetime.combine(datetime.date.today(), clock.time()).timestamp()),
            write_precision=WritePrecision.S)))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__write_api.close()
        self.__client.close()
