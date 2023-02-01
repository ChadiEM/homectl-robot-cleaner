import os

from cleaner.condition import Condition
from cleaner.scanner import NetworkScanner

HOME_IPS = os.getenv('HOME_IPS', '')


class AreHostsOutside(Condition):
    def __init__(self, scanner: NetworkScanner):
        super().__init__(True)
        self.scanner = scanner

    def is_satisfied(self) -> bool:
        ips = HOME_IPS.split(',')
        for ip in ips:
            status_response = self.scanner.get_status(ip)
            if status_response.status == 'up':
                return False
        return True
