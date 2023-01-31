import logging

from cleaner.condition import Condition
from cleaner.conditions.hosts_outside import AreHostsOutside
from cleaner.conditions.not_cleaned_today import NotCleanedToday
from cleaner.conditions.someone_home_last_day import SomeoneHomeInTheLastDay
from cleaner.conditions.time import Time
from cleaner.influx_client import InfluxClient
from cleaner.rowenta_client import RowentaClient

logger = logging.getLogger(__name__)


def start_if_needed():
    logger.info('Started.')

    with InfluxClient() as influx_client:
        conditions: list[Condition] = [
            Time(),
            NotCleanedToday(influx_client),
            AreHostsOutside(),
            SomeoneHomeInTheLastDay()
        ]

        def done():
            influx_client.mark_cleaned()

        rowenta_client = RowentaClient()
        rowenta_client.clean(done, conditions)
