import os
import time
from datetime import timedelta

from cleaner.condition import Condition
from cleaner.scanner import NetworkScanner

HOME_IPS = os.getenv('HOME_IPS', '')
NETWORK_SCANNER_ENDPOINT = os.getenv('NETWORK_SCANNER_ENDPOINT')


class SomeoneHomeInTheLastDay(Condition):
    """If there is no activity in the last 24 hours, do not clean"""

    def __init__(self, scanner: NetworkScanner):
        self.scanner = scanner

    def is_satisfied(self) -> bool:
        current_time = time.time()
        one_day = timedelta(hours=24).total_seconds()

        ips = HOME_IPS.split(',')
        for ip in ips:
            status_response = self.scanner.get_status(ip)
            if status_response.status == 'down' and (current_time - status_response.last_seen) < one_day:
                return True
        return False

    def should_recheck(self) -> bool:
        return False
