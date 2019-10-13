import pytest
from sqlalchemy.orm.exc import NoResultFound
from pipsy.entities import UserProject


@pytest.fixture(scope="module")
def userproject(project, user):
    try:
        return UserProject.find_one(user=user, project=project)
    except NoResultFound:
        return UserProject.create(user=user, project=project)


def test_cls_name():
    assert UserProject.cls_name() == 'UserProject'


def test_user(userproject, user):
    assert userproject.user == user


def test_project(userproject, project):
    assert userproject.project == project


def test_find_one(userproject):
    assert userproject == UserProject.find_one(user=userproject.user,
                                               project=userproject.project)


def test_find_user(userproject, user):
    assert userproject in UserProject.find(user=user)


def test_find_project(userproject, project):
    assert userproject in UserProject.find(project=project)


def test_task_user_assignment(project, user):
    user.projects = [project]
    assert project in user.projects
    user.projects = []
    assert user.projects == []
    user.projects += [project]
    assert project in user.projects
    user.projects -= project
    assert project not in user.projects
    user.projects = [project]
    assert project in user.projects


def test_assign_projects_to_user(user, project):
    UserProject.assign_projects_to_user(user, [project])
