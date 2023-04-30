import logging
import signal

from cleaner import robot_cleaner
from cleaner.influx_client import InfluxAPIClient
from cleaner.rowenta_client import RequestsRowentaClient
from cleaner.scanner import RequestsNetworkScanner

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)


def main():
    logger.info('Started.')

    with InfluxAPIClient() as influx_client:
        robot_cleaner.start(influx_client, RequestsNetworkScanner(), RequestsRowentaClient())


def interrupt():
    robot_cleaner.interrupt()


def __stop(_signum, _frame):
    interrupt()


signal.signal(signal.SIGINT, __stop)

if __name__ == '__main__':
    main()
