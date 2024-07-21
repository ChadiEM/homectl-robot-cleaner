from cleaner.condition import Condition
from cleaner.rowenta_client import RowentaClient


class RobotDocked(Condition):
    """If the robot is not docked (failed previous activity), do not run """

    def __init__(self, rowenta_client: RowentaClient):
        super().__init__(False)
        self.rowenta_client = rowenta_client

    def is_satisfied(self) -> bool:
        return self.rowenta_client.is_docked()
