import pytest
from sqlalchemy.orm.exc import NoResultFound
from pipsy.entities import Format


@pytest.fixture(scope="module")
def format(project):
    try:
        return Format.find_one(entity=project)
    except NoResultFound:
        return Format.create(entity=project)


def test_cls_name():
    assert Format.cls_name() == 'Format'


def test_project(format, project):
    assert format.project_id == project.id
    assert format.project == project


def test_find(format):
    assert format in Format.find()


def test_findby_ids(format):
    assert format in Format.findby_ids([format.id])


def test_find_one(format):
    assert format == Format.find_one(id=format.id)
