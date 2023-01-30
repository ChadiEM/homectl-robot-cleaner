import os
import time
from datetime import timedelta

import requests

from condition import Condition

HOME_IPS = os.getenv('HOME_IPS')
NETWORK_SCANNER_ENDPOINT = os.getenv('NETWORK_SCANNER_ENDPOINT')


class SomeoneHomeInTheLastDay(Condition):
    """If there is no activity in the last 24 hours, do not clean"""

    def is_satisfied(self) -> bool:
        current_time = time.time()
        one_day = timedelta(hours=24).total_seconds()

        ips = HOME_IPS.split(',')
        for ip in ips:
            response = requests.get(f'{NETWORK_SCANNER_ENDPOINT}/network/ip/{ip}').json()
            if response['status'] == 'down' and (current_time - response['last_seen']) < one_day:
                return True
        return False

    def should_recheck(self) -> bool:
        return False
