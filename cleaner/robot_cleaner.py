import datetime
import logging
import threading

from cleaner.condition import Condition
from cleaner.conditions.hosts_outside import AreHostsOutside
from cleaner.conditions.not_cleaned_today import NotCleanedToday
from cleaner.conditions.robot_docked import RobotDocked
from cleaner.conditions.someone_home_last_day import SomeoneHomeInTheLastDay
from cleaner.conditions.time import Time
from cleaner.conditions.time_bounds import START
from cleaner.influx_client import InfluxClient
from cleaner.rowenta_client import RowentaClient, RowentaCleaner, CleaningResult
from cleaner.scanner import NetworkScanner

logger = logging.getLogger(__name__)
interrupted_event = threading.Event()

CLEAN_CHECK_INTERVAL = datetime.timedelta(minutes=1)


def sleep_until_tomorrow():
    now = datetime.datetime.now()
    next_run = datetime.datetime.combine(now, START)

    if now > next_run:
        next_run = next_run + datetime.timedelta(days=1)

    print(f'Sleeping until {str(next_run)}')
    interrupted_event.wait((next_run - now).total_seconds())


def start(influx_client: InfluxClient, network_scanner: NetworkScanner, rowenta_client: RowentaClient):
    logger.info('Cleaner started.')

    conditions: list[Condition] = [
        Time(),
        NotCleanedToday(influx_client),
        AreHostsOutside(network_scanner),
        SomeoneHomeInTheLastDay(network_scanner),
        RobotDocked(rowenta_client)
    ]

    rowenta_cleaner = RowentaCleaner(rowenta_client)

    if influx_client.has_cleaned_today():
        sleep_until_tomorrow()

    while not interrupted_event.is_set():
        cleaning_result = rowenta_cleaner.clean(conditions, interrupted_event)

        if cleaning_result == CleaningResult.SUCCESS:
            influx_client.mark_cleaned_today()
            sleep_until_tomorrow()
        elif cleaning_result == CleaningResult.FAILURE_DO_NOT_RETRY:
            sleep_until_tomorrow()
        elif cleaning_result == CleaningResult.FAILURE:
            logger.info(f'Next check in {CLEAN_CHECK_INTERVAL.total_seconds()} seconds.')
            interrupted_event.wait(CLEAN_CHECK_INTERVAL.total_seconds())
        else:
            raise Exception('Invalid cleaning result.')


def interrupt():
    logger.info('Cleaner interrupted!')
    interrupted_event.set()
