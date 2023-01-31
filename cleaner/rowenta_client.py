import logging
import os
import time
from datetime import date

import requests

from cleaner.condition import Condition

ROWENTA_HOSTNAME = os.getenv('ROWENTA_HOSTNAME')
logger = logging.getLogger(__name__)


def _is_today(task):
    start_time = task['start_time']
    today = date.today()
    return today.year == start_time['year'] \
        and today.month == start_time['month'] \
        and today.day == start_time['day']


class RowentaClient:
    def _find_task(self, command_id):
        response = requests.get(f'http://{ROWENTA_HOSTNAME}:8080/get/task_history')

        if response.ok:
            history_arr = response.json()['task_history']

            for task in reversed(history_arr):
                if task['source_id'] == command_id and _is_today(task):
                    return task

        return None

    def _is_finished(self, command_id):
        task = self._find_task(command_id)
        if task is None:
            return False

        state = task['state']

        if state == 'done' or 'interrupted' in state:
            return True

        return False

    def clean(self, done, conditions: list[Condition]):
        for condition in conditions:
            if not condition.is_satisfied():
                logger.info(f'Condition {type(condition).__name__} not satisfied. Skipping.')
                return

        running_conditions = filter(lambda c: c.should_recheck(), conditions)

        response = requests.get(f'http://{ROWENTA_HOSTNAME}:8080/set/clean_map?map_id=3')

        if response.ok:
            logger.info('Started cleaning...')

            cmd_id = response.json()['cmd_id']

            while True:
                for condition in running_conditions:
                    if not condition.is_satisfied():
                        logger.info(f'Condition {type(condition).__name__} not satisfied. Cleaning interrupted.')
                        requests.get(f'http://{ROWENTA_HOSTNAME}:8080/set/go_home')
                        return

                if self._is_finished(cmd_id):
                    break

                time.sleep(10)

            logger.info('Cleaning finished. See you tomorrow!')

            done()
