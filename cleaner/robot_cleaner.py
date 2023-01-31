from cleaner.condition import Condition
from cleaner.conditions.hosts_outside import AreHostsOutside
from cleaner.conditions.not_cleaned_today import NotCleanedToday
from cleaner.conditions.someone_home_last_day import SomeoneHomeInTheLastDay
from cleaner.conditions.time import Time
from cleaner.influx_client import InfluxClient
from cleaner.rowenta_client import RowentaClient, RowentaCleaner, CleaningResult
from cleaner.scanner import NetworkScanner


def start(influx_client: InfluxClient, network_scanner: NetworkScanner, rowenta_client: RowentaClient):
    conditions: list[Condition] = [
        Time(),
        NotCleanedToday(influx_client),
        AreHostsOutside(network_scanner),
        SomeoneHomeInTheLastDay(network_scanner)
    ]

    rowenta_cleaner = RowentaCleaner(rowenta_client)

    cleaning_result = rowenta_cleaner.clean(conditions)

    if cleaning_result == CleaningResult.SUCCESS:
        influx_client.mark_cleaned()
