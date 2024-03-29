from sqlalchemy.exc import IntegrityError
from pipsy.core.pythonx import string_types
from pipsy.entities import Shot


def test_cls_name():
    assert Shot.cls_name() == 'Shot'


def test_project(shot, sequence):
    assert shot.sequence == sequence
    assert shot.project == sequence.project
    assert shot.sequence_id == sequence.id


def test_parent_project(shot, sequence):
    assert shot.parent == sequence


def test_parent_sequence(shot, sequence):
    assert shot.parent == sequence


def test_parent_sequence_episode(shot_episode, sequence_episode):
    assert shot_episode.parent == sequence_episode
    assert shot_episode.parent.parent == sequence_episode.parent
    assert shot_episode.parent.parent == sequence_episode.episode


def test_find(shot):
    assert shot in Shot.find()


def test_findby_ids(shot):
    assert shot in Shot.findby_ids([shot.id])


def test_find_one(shot):
    assert shot == Shot.find_one(id=shot.id)


def test_findby_name(shot):
    assert shot == Shot.find_one(project=shot.project,
                                 sequence=shot.sequence,
                                 name=shot.name)


def test_create_unique_proj_seq_name(shot):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        Shot.create(name=shot.name, project=shot.sequence.project, sequence=shot.sequence)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')


def test_cut(shot):
    assert isinstance(shot.cut, tuple)
    assert shot.cut == (shot.cut_in, shot.cut_out)


def test_fullname(shot):
    assert isinstance(shot.fullname, string_types)


def test_fullname_episode(shot_episode):
    assert isinstance(shot_episode.fullname, string_types)
