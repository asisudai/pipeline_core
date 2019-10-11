import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from pipsy.entities import Episode, Sequence


@pytest.fixture(scope="module")
def sequence(project):
    try:
        return Sequence.find_one(project=project, name='101')
    except NoResultFound:
        return Sequence.create(project=project, name='101')


@pytest.fixture(scope="module")
def episode(project):
    try:
        return Episode.find_one(project=project, name='101')
    except NoResultFound:
        return Episode.create(project=project, name='101')


@pytest.fixture(scope="module")
def sequence_episode(episode):
    try:
        return Sequence.find_one(episode=episode, name='101')
    except NoResultFound:
        return Sequence.create(project=episode.project, episode=episode, name='101')


def test_cls_name():
    assert Sequence.cls_name() == 'Sequence'


def test_project(sequence, project):
    assert sequence.project_id == project.id
    assert sequence.project == project


def test_parent_project(sequence, project):
    assert sequence.parent == project


def test_parent_episode(sequence_episode):
    assert sequence_episode.parent == sequence_episode.episode


def test_find(sequence):
    assert sequence in Sequence.find()


def test_findby_ids(sequence):
    assert sequence in Sequence.findby_ids([sequence.id])


def test_find_one(sequence):
    assert sequence == Sequence.find_one(id=sequence.id)


def test_episode_id_virtual(sequence):
    assert sequence.episode_id_virtual == (sequence.episode_id or 0)


def test_sequence_episode(sequence_episode, episode):
    assert sequence_episode.episode == episode
    assert sequence_episode.episode_id == episode.id
    assert sequence_episode.project == sequence_episode.project


def test_create_unique_proj_name(sequence):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        Sequence.create(name=sequence.name, project=sequence.project)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')


def test_create_unique_proj_ep_name(sequence_episode):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        Sequence.create(name=sequence_episode.name, project=sequence_episode.project,
                        episode=sequence_episode.episode)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')
