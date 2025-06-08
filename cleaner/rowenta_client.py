import abc
import datetime
import logging
import os
import threading
from datetime import date
from enum import Enum, auto, Flag

import requests

from cleaner.condition import Condition
from cleaner.rowenta_client_types import CleanResponse, TaskHistoryResponse, StatusModel, TaskHistoryItem

logger = logging.getLogger(__name__)


def _is_today(task: TaskHistoryItem) -> bool:
    start_time = task.start_time
    today = date.today()
    return today.year == start_time.year \
        and today.month == start_time.month \
        and today.day == start_time.day


class TaskStatus(Flag):
    NOT_STARTED = auto()
    RUNNING = auto()
    INTERRUPTED_BY_USER = auto()
    INTERRUPTED_STUCK_WHEELS = auto()
    INTERRUPTED_OTHER = auto()
    FAILED = auto()
    FINISHED_SUCCESS = auto()

    FINISHED = INTERRUPTED_BY_USER | INTERRUPTED_STUCK_WHEELS | INTERRUPTED_OTHER | FAILED | FINISHED_SUCCESS
    FAILURE = INTERRUPTED_STUCK_WHEELS | INTERRUPTED_OTHER | FAILED
    RETRIABLE_FAILURE = INTERRUPTED_BY_USER


class RowentaClient(abc.ABC):
    @abc.abstractmethod
    def clean_house(self) -> int | None:
        pass

    @abc.abstractmethod
    def go_home(self) -> None:
        pass

    @abc.abstractmethod
    def task_status(self, cmd_id: int) -> TaskStatus:
        pass

    @abc.abstractmethod
    def is_docked(self) -> bool:
        pass


class RequestsRowentaClient(RowentaClient):
    def __init__(self) -> None:
        self.rowenta_endpoint = os.getenv('ROWENTA_ENDPOINT')

    def _find_task(self, command_id: int) -> TaskHistoryItem | None:
        response = requests.get(f'{self.rowenta_endpoint}/get/task_history', timeout=5)
        if response.ok:
            res = TaskHistoryResponse.model_validate_json(response.content)
            history_arr = res.task_history
            for task in reversed(history_arr):
                if task.source_id == command_id and _is_today(task):
                    return task
        return None

    def clean_house(self) -> int | None:
        response = requests.get(f'{self.rowenta_endpoint}/set/clean_map?map_id=11', timeout=5)
        if response.ok:
            res = CleanResponse.model_validate_json(response.content)
            return res.cmd_id
        return None

    def go_home(self) -> None:
        requests.get(f'{self.rowenta_endpoint}/set/go_home', timeout=5)

    def task_status(self, cmd_id: int) -> TaskStatus:
        task = self._find_task(cmd_id)
        if task is None:
            return TaskStatus.NOT_STARTED

        state = task.state

        if state == 'done':
            return TaskStatus.FINISHED_SUCCESS

        if state == 'interrupted_stuck_wheels':
            return TaskStatus.INTERRUPTED_STUCK_WHEELS

        if state == 'interrupted_by_user':
            return TaskStatus.INTERRUPTED_BY_USER

        if 'interrupted' in state:
            return TaskStatus.INTERRUPTED_OTHER

        if state == 'failed':
            return TaskStatus.FAILED

        return TaskStatus.RUNNING

    def is_docked(self) -> bool:
        response = requests.get(f'{self.rowenta_endpoint}/get/status', timeout=5)
        res = StatusModel.model_validate_json(response.content)
        return res.mode == 'ready' and res.charging != 'unconnected'


class CleaningResult(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    FAILURE_DO_NOT_RETRY = auto()


class RowentaCleaner:
    RECHECK_SECONDS = datetime.timedelta(seconds=5)

    def __init__(self, rowenta_client: RowentaClient):
        self.rowenta_client = rowenta_client

    def clean(self, conditions: list[Condition], interrupted: threading.Event) -> CleaningResult:
        for condition in conditions:
            if not condition.is_satisfied():
                logger.info(f'Condition {type(condition).__name__} not satisfied. Skipping.')
                return CleaningResult.FAILURE

        running_conditions = list(filter(lambda c: c.should_recheck(), conditions))

        cmd_id = self.rowenta_client.clean_house()
        if cmd_id is None:
            logger.info('Cleaning request failed. Will reattempt later.')
            return CleaningResult.FAILURE

        logger.info('Started cleaning...')

        status = TaskStatus.NOT_STARTED

        while not interrupted.is_set():
            for condition in running_conditions:
                if not condition.is_satisfied():
                    logger.info(f'Condition {type(condition).__name__} not satisfied. Cleaning interrupted.')
                    self.rowenta_client.go_home()
                    return CleaningResult.FAILURE

            status = self.rowenta_client.task_status(cmd_id)

            if status in TaskStatus.FINISHED:
                break

            interrupted.wait(RowentaCleaner.RECHECK_SECONDS.total_seconds())

        if status == TaskStatus.FINISHED_SUCCESS:
            logger.info('Cleaning finished successfully. See you tomorrow!')
            return CleaningResult.SUCCESS
        elif status in TaskStatus.FAILURE:
            logger.info('Cleaning failed. Will wait until tomorrow.')
            return CleaningResult.FAILURE_DO_NOT_RETRY
        elif status in TaskStatus.RETRIABLE_FAILURE:
            logger.info('Cleaning interrupted. Will reattempt later.')
            return CleaningResult.FAILURE
        else:
            raise Exception(f'Unexpected status: {status}')
