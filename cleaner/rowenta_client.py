import abc
import logging
import os
import time
from datetime import date
from enum import Enum

import requests

from cleaner.condition import Condition

logger = logging.getLogger(__name__)


def _is_today(task):
    start_time = task['start_time']
    today = date.today()
    return today.year == start_time['year'] \
        and today.month == start_time['month'] \
        and today.day == start_time['day']


class RowentaClient(abc.ABC):
    @abc.abstractmethod
    def clean_house(self) -> int:
        pass

    @abc.abstractmethod
    def go_home(self) -> None:
        pass

    @abc.abstractmethod
    def is_task_finished(self, cmd_id: int) -> bool:
        pass


class RequestsRowentaClient(RowentaClient):
    def __init__(self):
        self.rowenta_endpoint = os.getenv('ROWENTA_ENDPOINT')

    def _find_task(self, command_id):
        response = requests.get(f'{self.rowenta_endpoint}/get/task_history', timeout=60)
        if response.ok:
            history_arr = response.json()['task_history']
            for task in reversed(history_arr):
                if task['source_id'] == command_id and _is_today(task):
                    return task
        return None

    def clean_house(self) -> int:
        response = requests.get(f'{self.rowenta_endpoint}/set/clean_map?map_id=3', timeout=60)
        return response.json()['cmd_id']

    def go_home(self) -> None:
        requests.get(f'{self.rowenta_endpoint}/set/go_home', timeout=60)

    def is_task_finished(self, cmd_id: int) -> bool:
        task = self._find_task(cmd_id)
        if task is None:
            return False

        state = task['state']

        if state == 'done' or 'interrupted' in state:
            return True

        return False


class CleaningResult(Enum):
    SUCCESS = 1
    FAILURE = 2


class RowentaCleaner:
    def __init__(self, rowenta_client: RowentaClient):
        self.rowenta_client = rowenta_client

    def clean(self, conditions: list[Condition]) -> CleaningResult:
        for condition in conditions:
            if not condition.is_satisfied():
                logger.info(f'Condition {type(condition).__name__} not satisfied. Skipping.')
                return CleaningResult.FAILURE

        running_conditions = filter(lambda c: c.should_recheck(), conditions)

        cmd_id = self.rowenta_client.clean_house()

        logger.info('Started cleaning...')

        while True:
            for condition in running_conditions:
                if not condition.is_satisfied():
                    logger.info(f'Condition {type(condition).__name__} not satisfied. Cleaning interrupted.')
                    self.rowenta_client.go_home()
                    return CleaningResult.FAILURE

            if self.rowenta_client.is_task_finished(cmd_id):
                break

            time.sleep(10)

        logger.info('Cleaning finished. See you tomorrow!')

        return CleaningResult.SUCCESS
