import datetime
import os
import threading
import time
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from influxdb_client import InfluxDBClient
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs
from werkzeug.serving import make_server

import cleaner.main
from influx_version import INFLUX_CONTAINER_IMAGE_VERSION


class ServerThread(threading.Thread):
    def __init__(self, app, port):
        threading.Thread.__init__(self)
        self.server = make_server('127.0.0.1', port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()


@pytest.fixture
def network_scanner():
    app = Flask(__name__)

    @app.route('/network/ip/')
    def status():
        return {
            "status": "down",
            "last_seen": time.time() - datetime.timedelta(hours=10).total_seconds()
        }

    server = ServerThread(app, 33000)
    server.start()

    yield app

    server.shutdown()


@pytest.fixture
def rowenta():
    app = Flask(__name__)

    last_command = 0
    history_request = 0

    @app.route('/set/go_home')
    def go_home():
        nonlocal last_command
        last_command = last_command + 1
        return {
            "cmd_id": last_command
        }

    @app.route('/set/clean_map')
    def clean_map():
        nonlocal last_command
        last_command = last_command + 1
        return {
            "cmd_id": last_command
        }

    @app.route('/get/task_history')
    def task_history():
        nonlocal history_request
        history_request = history_request + 1

        today = datetime.date.today()

        if history_request == 1:
            return {
                "task_history": [
                    {
                        "id": 898,
                        "task_type_id": 1,
                        "task_type": "clean_map",
                        "strategy": "none",
                        "cleaning_parameter_set": 0,
                        "map_id": 3,
                        "area_ids": [],
                        "source": "user",
                        "source_id": 1,
                        "start_time": {"year": today.year, "month": today.month, "day": today.day,
                                       "hour": 11, "min": 15, "sec": 26},
                        "end_time": {"year": 0, "month": 0, "day": 0, "hour": 0, "min": 0, "sec": 0},
                        "state_id": 0,
                        "state": "executing",
                        "area": 0,
                        "continuable": 0,
                        "event_history": [],
                        "area_history": [],
                        "firmware": "SER80-1.2.3-release:3.9.2804"
                    },
                ],
                "task_requires_map_confirmation": 0,
                "task_requires_special_area_confirmation": 0
            }
        else:
            return {
                "task_history": [
                    {
                        "id": 898,
                        "task_type_id": 1,
                        "task_type": "clean_map",
                        "strategy": "none",
                        "cleaning_parameter_set": 0,
                        "map_id": 3,
                        "area_ids": [],
                        "source": "user",
                        "source_id": 1,
                        "start_time": {"year": today.year, "month": today.month, "day": today.day,
                                       "hour": 11, "min": 15, "sec": 26},
                        "end_time": {"year": today.year, "month": today.month, "day": today.day,
                                     "hour": 11, "min": 35, "sec": 45},
                        "state_id": 1,
                        "state": "done",
                        "area": 4520000,
                        "continuable": 0,
                        "event_history": [],
                        "area_history": [
                            {
                                "area_id": 6,
                                "start_time": {"year": 2023, "month": 2, "day": 16, "hour": 13, "min": 20, "sec": 11},
                                "end_time": {"year": 2023, "month": 2, "day": 16, "hour": 13, "min": 24, "sec": 9},
                                "state_id": 1,
                                "state": "done"
                            },
                            {
                                "area_id": 7,
                                "start_time": {"year": 2023, "month": 2, "day": 16, "hour": 13, "min": 24, "sec": 9},
                                "end_time": {"year": 2023, "month": 2, "day": 16, "hour": 13, "min": 26, "sec": 42},
                                "state_id": 1,
                                "state": "done"
                            },
                            {
                                "area_id": 16,
                                "start_time": {"year": 2023, "month": 2, "day": 16, "hour": 13, "min": 26, "sec": 42},
                                "end_time": {"year": 2023, "month": 2, "day": 16, "hour": 13, "min": 28, "sec": 31},
                                "state_id": 1,
                                "state": "done"
                            },
                            {
                                "area_id": 10,
                                "start_time": {"year": 2023, "month": 2, "day": 16, "hour": 13, "min": 28, "sec": 31},
                                "end_time": {"year": 2023, "month": 2, "day": 16, "hour": 13, "min": 37, "sec": 18},
                                "state_id": 1,
                                "state": "done"
                            },
                            {
                                "area_id": 14,
                                "start_time": {"year": 2023, "month": 2, "day": 16, "hour": 13, "min": 37, "sec": 18},
                                "end_time": {"year": 2023, "month": 2, "day": 16, "hour": 13, "min": 39, "sec": 2},
                                "state_id": 1,
                                "state": "done"
                            }
                        ],
                        "firmware": "SER80-1.2.3-release:3.9.2804"
                    },
                ],
                "task_requires_map_confirmation": 0,
                "task_requires_special_area_confirmation": 0
            }

    @app.route('/get/status')
    def get_status():
        return {
            "voltage": 15920,
            "mode": "ready",
            "cleaning_parameter_set": 3,
            "battery_level": 89,
            "charging": "connected",
            "time": {"year": 2024, "month": 7, "day": 21, "hour": 10, "min": 40, "sec": 5, "day_of_week": 7},
            "startup_time": {"year": 2024, "month": 7, "day": 21, "hour": 5, "min": 47, "sec": 37, "day_of_week": 7}
        }

    server = ServerThread(app, 33001)
    server.start()

    yield app

    server.shutdown()


@pytest.fixture(scope="function")
def my_variable(monkeypatch):
    monkeypatch.setenv("INFLUXDB_V2_URL", 'http://localhost:8086')
    monkeypatch.setenv("INFLUXDB_V2_TOKEN", 'admin-token')
    monkeypatch.setenv("INFLUXDB_V2_ORG", 'influxdata')
    monkeypatch.setenv("ROBOT_CLEANER_INFLUX_BUCKET", 'data')
    monkeypatch.setenv("NETWORK_SCANNER_ENDPOINT", 'http://localhost:33000')
    monkeypatch.setenv("ROWENTA_ENDPOINT", 'http://localhost:33001')


def assert_cleaned():
    start_time_check = datetime.datetime.now()

    start_ts = int(datetime.datetime.combine(datetime.date.today(), datetime.time(11)).timestamp())
    stop_ts = int(datetime.datetime.combine(datetime.date.today(), datetime.time(12)).timestamp())

    with InfluxDBClient.from_env_properties() as influx_client:
        bucket = os.environ.get('ROBOT_CLEANER_INFLUX_BUCKET')
        query_api = influx_client.query_api()

        while datetime.datetime.now() - start_time_check < datetime.timedelta(seconds=60):
            result = query_api.query(f"""from(bucket:"{bucket}")
                    |> range(start: {start_ts}, stop: {stop_ts})
                    |> filter(fn:(r) => r._measurement == "home_control" and r._field == "robot-clean")""")

            if len(result) == 0:
                time.sleep(1)
            else:
                break

        assert len(result) > 0


@patch('cleaner.clock.time', Mock(return_value=datetime.time(11, 15, 26)))
def test_e2e(my_variable, network_scanner, rowenta):
    with DockerContainer(INFLUX_CONTAINER_IMAGE_VERSION) \
            .with_env("DOCKER_INFLUXDB_INIT_MODE", "setup") \
            .with_env("DOCKER_INFLUXDB_INIT_USERNAME", "admin") \
            .with_env("DOCKER_INFLUXDB_INIT_PASSWORD", "password") \
            .with_env("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN", "admin-token") \
            .with_env("DOCKER_INFLUXDB_INIT_ORG", "influxdata") \
            .with_env("DOCKER_INFLUXDB_INIT_BUCKET", "data") \
            .with_bind_ports(8086, 8086) \
            as container:
        wait_for_logs(container, "transport=http addr=:8086 port=8086")

        print(container.get_logs())

        t = threading.Thread(target=cleaner.main.main)
        t.start()

        try:
            assert_cleaned()
        finally:
            cleaner.main.interrupt()
