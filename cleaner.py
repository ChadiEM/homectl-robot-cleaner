import logging
import os
import time
from datetime import date

import requests

from condition import Condition
from conditions.hosts_outside import AreHostsOutside
from conditions.not_cleaned_today import NotCleanedToday
from conditions.someone_home_last_day import SomeoneHomeInTheLastDay
from conditions.time import Time
from influx_client import InfluxClient

ROWENTA_HOSTNAME = os.getenv('ROWENTA_HOSTNAME')

logger = logging.getLogger(__name__)


def is_today(task):
    start_time = task['start_time']
    today = date.today()
    return today.year == start_time['year'] and today.month == start_time['month'] and today.day == start_time['day']


def find_task(command_id):
    response = requests.get(f'http://{ROWENTA_HOSTNAME}:8080/get/task_history')

    if response.ok:
        history_arr = response.json()['task_history']

        for task in reversed(history_arr):
            if task['source_id'] == command_id and is_today(task):
                return task

    return None


def is_finished(command_id):
    task = find_task(command_id)
    if task is None:
        return False

    state = task['state']

    if state == 'done' or 'interrupted' in state:
        return True

    return False


def clean(influx_client: InfluxClient, conditions: list[Condition]):
    response = requests.get(f'http://{ROWENTA_HOSTNAME}:8080/set/clean_map?map_id=3')

    if response.ok:
        logger.info('Started cleaning...')

        cmd_id = response.json()['cmd_id']

        while True:
            for condition in conditions:
                if not condition.is_satisfied():
                    logger.info(f'Condition {type(condition).__name__} not satisfied. Cleaning interrupted.')
                    requests.get(f'http://{ROWENTA_HOSTNAME}:8080/set/go_home')
                    return

            if is_finished(cmd_id):
                break

            time.sleep(10)

        logger.info('Cleaning finished. See you tomorrow!')

        influx_client.mark_cleaned()


def start_if_needed():
    logger.info('Started.')

    with InfluxClient() as influx_client:
        conditions: list[Condition] = [
            Time(),
            NotCleanedToday(influx_client),
            AreHostsOutside(),
            SomeoneHomeInTheLastDay()
        ]

        running_conditions: list[Condition] = [
            AreHostsOutside()
        ]

        for condition in conditions:
            if not condition.is_satisfied():
                logger.info(f'Condition {type(condition).__name__} not satisfied. Skipping.')
                return

        clean(influx_client, running_conditions)
