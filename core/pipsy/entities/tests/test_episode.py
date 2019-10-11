import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from pipsy.entities import Episode


@pytest.fixture(scope="module")
def episode(project):
    try:
        return Episode.find_one(project=project, name='101')
    except NoResultFound:
        return Episode.create(project=project, name='101')


def test_cls_name():
    assert Episode.cls_name() == 'Episode'


def test_project(episode, project):
    assert episode.project_id == project.id
    assert episode.project == project


def test_parent_project(episode, project):
    assert episode.parent == project


def test_find(episode):
    assert episode in Episode.find()


def test_findby_ids(episode):
    assert episode in Episode.findby_ids([episode.id])


def test_find_one(episode):
    assert episode == Episode.find_one(id=episode.id)


def test_create_unique_proj_name(episode, session):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        Episode.create(name=episode.name, project=episode.project)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')
