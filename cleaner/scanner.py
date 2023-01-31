import abc
import os
from dataclasses import dataclass

import requests

NETWORK_SCANNER_ENDPOINT = os.getenv('NETWORK_SCANNER_ENDPOINT')


@dataclass
class StatusResponse:
    status: str
    last_seen: int


class NetworkScanner(abc.ABC):
    @abc.abstractmethod
    def get_status(self, ip: str) -> StatusResponse:
        pass


class RequestsNetworkScanner(NetworkScanner):
    def get_status(self, ip: str) -> StatusResponse:
        response = requests.get(f'{NETWORK_SCANNER_ENDPOINT}/network/ip/{ip}').json()
        return StatusResponse(response['status'], response['last_seen'])
