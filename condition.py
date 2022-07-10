import abc


class Condition(abc.ABC):
    @abc.abstractmethod
    def is_satisfied(self):
        pass
