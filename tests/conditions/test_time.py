from datetime import time
from unittest.mock import Mock, patch

from cleaner.conditions.time import Time


@patch('cleaner.clock.time', Mock(return_value=time(9, 45, 5)))
def test_should_fail_condition_in_the_morning():
    assert not Time().is_satisfied()


@patch('cleaner.clock.time', Mock(return_value=time(11, 15, 26)))
def test_should_pass_condition_during_the_day():
    assert Time().is_satisfied()


@patch('cleaner.clock.time', Mock(return_value=time(22, 15, 26)))
def test_should_fail_condition_in_the_evening():
    assert not Time().is_satisfied()
