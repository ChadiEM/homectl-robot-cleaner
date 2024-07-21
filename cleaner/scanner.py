import abc
import os
from dataclasses import dataclass

import httpx


@dataclass
class StatusResponse:
    status: str
    last_seen: int


class NetworkScanner(abc.ABC):
    @abc.abstractmethod
    def get_status(self, ip: str) -> StatusResponse:
        pass


class RequestsNetworkScanner(NetworkScanner):
    def __init__(self):
        self.scanner_endpoint = os.getenv('NETWORK_SCANNER_ENDPOINT')

    def get_status(self, ip: str) -> StatusResponse:
        response = httpx.get(f'{self.scanner_endpoint}/network/ip/{ip}', timeout=60).json()
        return StatusResponse(response['status'], response['last_seen'])
