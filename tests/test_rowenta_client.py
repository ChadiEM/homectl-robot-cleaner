from cleaner.rowenta_client import TaskStatus


def test_should_have_finished_in_finished_success():
    status = TaskStatus.FINISHED_SUCCESS
    assert status in TaskStatus.FINISHED


def test_should_have_finished_in_finished_failure():
    status = TaskStatus.FINISHED_FAILURE
    assert status in TaskStatus.FINISHED
