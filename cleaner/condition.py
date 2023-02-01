import abc


class Condition(abc.ABC):
    def __init__(self, should_recheck_when_running: bool):
        self.should_recheck_when_running = should_recheck_when_running

    @abc.abstractmethod
    def is_satisfied(self) -> bool:
        pass

    def should_recheck(self) -> bool:
        return self.should_recheck_when_running
