"""Slice 4: Goal progress.

Expected behaviour:

    completion % = completed tasks / countable tasks * 100

- A goal with zero tasks is 0% complete, not a division error.
- Cancelled tasks are excluded entirely (neither counted toward the
  total nor toward completed) — an abandoned task shouldn't drag down
  or otherwise skew a goal's progress.
- Tasks belonging to different milestones under the same goal are all
  counted together — progress is goal-wide, not per-milestone.
- The percentage is rounded to the nearest whole number.
"""

from app.domain.enums import TaskStatus
from app.domain.progress import calculate_goal_progress
from app.domain.task import Task


def make_task(status: TaskStatus, milestone_id: str | None = None) -> Task:
    task = Task(goal_id="goal-1", milestone_id=milestone_id, title="Some task")
    task.status = status
    return task


def test_progress_of_goal_with_zero_tasks():
    progress = calculate_goal_progress([])

    assert progress.total_tasks == 0
    assert progress.completed_tasks == 0
    assert progress.remaining_tasks == 0
    assert progress.completion_percentage == 0


def test_progress_of_goal_with_one_of_one_completed():
    tasks = [make_task(TaskStatus.COMPLETED)]

    progress = calculate_goal_progress(tasks)

    assert progress.total_tasks == 1
    assert progress.completed_tasks == 1
    assert progress.remaining_tasks == 0
    assert progress.completion_percentage == 100


def test_progress_of_goal_with_two_of_four_completed():
    tasks = [
        make_task(TaskStatus.COMPLETED),
        make_task(TaskStatus.COMPLETED),
        make_task(TaskStatus.TODO),
        make_task(TaskStatus.IN_PROGRESS),
    ]

    progress = calculate_goal_progress(tasks)

    assert progress.total_tasks == 4
    assert progress.completed_tasks == 2
    assert progress.remaining_tasks == 2
    assert progress.completion_percentage == 50


def test_progress_of_goal_with_all_tasks_completed():
    tasks = [make_task(TaskStatus.COMPLETED) for _ in range(3)]

    progress = calculate_goal_progress(tasks)

    assert progress.completed_tasks == 3
    assert progress.remaining_tasks == 0
    assert progress.completion_percentage == 100


def test_progress_excludes_cancelled_tasks_from_total_and_completed():
    tasks = [
        make_task(TaskStatus.COMPLETED),
        make_task(TaskStatus.COMPLETED),
        make_task(TaskStatus.CANCELLED),
        make_task(TaskStatus.TODO),
    ]

    progress = calculate_goal_progress(tasks)

    # 1 cancelled task is excluded entirely: 2 completed out of 3 countable.
    assert progress.total_tasks == 3
    assert progress.completed_tasks == 2
    assert progress.remaining_tasks == 1
    assert progress.completion_percentage == 67


def test_progress_of_goal_with_only_cancelled_tasks_is_zero_not_a_division_error():
    tasks = [make_task(TaskStatus.CANCELLED), make_task(TaskStatus.CANCELLED)]

    progress = calculate_goal_progress(tasks)

    assert progress.total_tasks == 0
    assert progress.completed_tasks == 0
    assert progress.completion_percentage == 0


def test_progress_counts_tasks_across_different_milestones_together():
    tasks = [
        make_task(TaskStatus.COMPLETED, milestone_id="milestone-1"),
        make_task(TaskStatus.TODO, milestone_id="milestone-1"),
        make_task(TaskStatus.COMPLETED, milestone_id="milestone-2"),
        make_task(TaskStatus.TODO, milestone_id="milestone-2"),
        make_task(TaskStatus.COMPLETED, milestone_id=None),  # directly on the goal
    ]

    progress = calculate_goal_progress(tasks)

    assert progress.total_tasks == 5
    assert progress.completed_tasks == 3
    assert progress.completion_percentage == 60


def test_progress_percentage_rounds_to_nearest_whole_number():
    tasks = [
        make_task(TaskStatus.COMPLETED),
        make_task(TaskStatus.TODO),
        make_task(TaskStatus.TODO),
    ]

    progress = calculate_goal_progress(tasks)

    assert progress.completion_percentage == 33
