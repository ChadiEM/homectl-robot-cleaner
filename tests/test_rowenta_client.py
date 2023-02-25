from unittest.mock import Mock, patch

from cleaner.condition import Condition
from cleaner.rowenta_client import TaskStatus, RowentaCleaner, RowentaClient, CleaningResult


def test_should_have_finished_in_finished_success():
    status = TaskStatus.FINISHED_SUCCESS
    assert status in TaskStatus.FINISHED


def test_should_have_finished_in_finished_failure():
    status = TaskStatus.FINISHED_FAILURE
    assert status in TaskStatus.FINISHED


@patch('cleaner.rowenta_client.RowentaCleaner.RECHECK_SECONDS', 0)
def test_running_conditions_should_be_reevaluated():
    rowenta_client = Mock(spec=RowentaClient)
    rowenta_client.clean_house.return_value = 1
    rowenta_client.task_status.return_value = TaskStatus.RUNNING

    condition = Mock(spec=Condition)
    condition.is_satisfied.side_effect = [True, True, False]
    condition.should_recheck.return_value = True

    cleaner = RowentaCleaner(rowenta_client)
    conditions = [condition]

    result = cleaner.clean(conditions)

    assert result == CleaningResult.FAILURE
