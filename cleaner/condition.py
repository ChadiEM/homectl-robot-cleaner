import abc


class Condition(abc.ABC):
    @abc.abstractmethod
    def is_satisfied(self) -> bool:
        pass

    @abc.abstractmethod
    def should_recheck(self) -> bool:
        pass
