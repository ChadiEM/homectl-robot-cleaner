import os
from datetime import datetime

import influxdb_client.client.write_api
from influxdb_client import InfluxDBClient, Point


class InfluxClient:
    def __init__(self):
        client = InfluxDBClient(url=os.environ.get('INFLUX_ENDPOINT'),
                                token=os.environ.get('INFLUX_TOKEN'),
                                org=os.environ.get('INFLUX_ORG'))

        self.__bucket = os.environ.get('INFLUX_BUCKET')

        self.__query_api = client.query_api()
        self.__write_api = client.write_api(write_options=influxdb_client.client.write_api.SYNCHRONOUS)

    def has_cleaned(self, start: datetime, end: datetime):
        start_ts = int(start.timestamp() * 1e9)
        stop_ts = int(end.timestamp() * 1e9)

        result = self.__query_api.query(f"""from(bucket:"{self.__bucket}")
        |> range(start: {start_ts}, stop: {stop_ts})
        |> filter(fn:(r) => r._measurement == "home_control" and r._field == "robot-clean")""")

        return len(result) == 0

    def mark_cleaned(self):
        self.__write_api.write(bucket=self.__bucket, record=(Point("home_control").field("robot-clean", True)))

    def __exit__(self):
        self.__write_api.close()
