from cleaner.condition import Condition


def test_condition_should_be_rechecked():
    class RecheckedTestCondition(Condition):
        def __init__(self):
            super().__init__(True)

        def is_satisfied(self) -> bool:
            return True

    c = RecheckedTestCondition()
    assert c.should_recheck()


def test_condition_should_not_be_rechecked():
    class NonRecheckedTestCondition(Condition):
        def __init__(self):
            super().__init__(False)

        def is_satisfied(self) -> bool:
            return True

    c = NonRecheckedTestCondition()
    assert not c.should_recheck()
