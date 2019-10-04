import pytest
from sqlalchemy.exc import IntegrityError
from pipsy.entities import Project


def test_cls_name():
    assert Project.cls_name() == 'Project'


def test_find(project):
    assert project in project.find()


def test_findby_ids(project):
    assert project in project.findby_ids([project.id])


def test_findby_name(project):
    assert project == project.findby_name(project.name)


def test_find_one(project):
    assert project == project.find_one(name=project.name)


@pytest.mark.xfail(raises=IntegrityError)
def test_create_unique_name(project):
    # Expecting IntegrityError error "Duplicate entry..."
    Project.create(name='unittest', root='/tmp/unittest2', schema='film')


@pytest.mark.xfail(raises=IntegrityError)
def test_create_unique_root(project):
    # Expecting IntegrityError error "Duplicate entry..."
    Project.create(name='unittest2', root='/tmp/unittest', schema='film')
