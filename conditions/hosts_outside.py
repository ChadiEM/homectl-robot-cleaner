import os

import requests

from condition import Condition

HOME_IPS = os.getenv('HOME_IPS')
NETWORK_SCANNER_ENDPOINT = os.getenv('NETWORK_SCANNER_ENDPOINT')


class AreHostsOutside(Condition):
    def is_satisfied(self):
        ips = HOME_IPS.split(',')
        for ip in ips:
            response = requests.get(f'{NETWORK_SCANNER_ENDPOINT}/network/ip/{ip}').json()
            if response['status'] == 'up':
                return False
        return True
