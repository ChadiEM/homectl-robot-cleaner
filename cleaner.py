import logging
import os
from datetime import datetime

import requests

from condition import Condition
from conditions.hosts_outside import AreHostsOutside
from conditions.not_cleaned_today import NotCleanedToday
from conditions.time import Time
from influx_client import InfluxClient

ROWENTA_HOSTNAME = os.getenv('ROWENTA_HOSTNAME')

logger = logging.getLogger(__name__)

START = datetime.today().replace(hour=10, minute=0, second=0, microsecond=0)  # 10 am
END = datetime.today().replace(hour=22, minute=0, second=0, microsecond=0)  # 10 pm


def clean(influx_client: InfluxClient):
    response = requests.get(
        f'http://{ROWENTA_HOSTNAME}:8080/set/clean_all?cleaning_parameter_set=0&cleaning_strategy_mode=4')

    if response.ok:
        influx_client.mark_cleaned()


def start_if_needed():
    with InfluxClient() as influx_client:
        conditions: list[Condition] = [
            Time(),
            NotCleanedToday(influx_client),
            AreHostsOutside()
        ]

        for condition in conditions:
            if not condition.is_satisfied():
                logger.info(f'Condition {type(condition).__name__} not satisfied. Skipping.')
                return

        clean(influx_client)
