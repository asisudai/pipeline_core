from sqlalchemy.exc import IntegrityError
from pipsy.entities import Episode


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
