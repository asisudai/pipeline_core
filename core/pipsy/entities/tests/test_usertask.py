import pytest
from sqlalchemy.orm.exc import NoResultFound
from pipsy.entities import UserTask


@pytest.fixture(scope="module")
def taskuser_shot(task_shot, user):
    try:
        return UserTask.find_one(task=task_shot, user=user)
    except NoResultFound:
        return UserTask.create(task=task_shot, user=user)


def test_cls_name():
    assert UserTask.cls_name() == 'UserTask'


def test_user(taskuser_shot, user):
    assert taskuser_shot.user == user


def test_task(taskuser_shot, task_shot):
    assert taskuser_shot.task == task_shot


def test_find_user(taskuser_shot, user):
    assert taskuser_shot in UserTask.find(user=user)


def test_find_task(taskuser_shot, task_shot):
    assert taskuser_shot in UserTask.find(task=task_shot)


def test_user_tasks(taskuser_shot, task_shot):
    assert task_shot in taskuser_shot.user.tasks


def test_task_users(taskuser_shot, user):
    assert user in taskuser_shot.task.users


def test_task_user_assignment(task_asset, user):
    task_asset.users = [user]
    assert task_asset.users == [user]
    task_asset.users = []
    assert task_asset.users == []
    task_asset.users = [user]
    assert task_asset.users == [user]
    task_asset.users -= user
    assert task_asset.users == []
    task_asset.users += user
    assert task_asset.users == [user]


def test_assign_users_to_task(task_asset, user):
    UserTask.assign_users_to_task(task_asset, [user])
