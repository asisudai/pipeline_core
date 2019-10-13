import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from pipsy.core.pythonx import string_types
from pipsy.entities import Instance


@pytest.fixture(scope="module")
def instance_shot(shot, asset):
    try:
        return Instance.find_one(project=shot.project, entity=shot,
                                 asset=asset, name='instance01')
    except NoResultFound:
        return Instance.create(project=shot.project, entity=shot,
                               asset=asset, name='instance01')


@pytest.fixture(scope="module")
def instance_sequence(sequence, asset):
    try:
        return Instance.find_one(project=sequence.project, entity=sequence,
                                 asset=asset, name='instance01')
    except NoResultFound:
        return Instance.create(project=sequence.project, entity=sequence,
                               asset=asset, name='instance01')


def test_fullname(instance_shot):
    assert isinstance(instance_shot.fullname, string_types)


def test_cls_name():
    assert Instance.cls_name() == 'Instance'


def test_asset(instance_shot, asset):
    assert instance_shot.asset == asset
    assert instance_shot.asset.id == asset.id


def test_parent_shot(instance_shot, shot):
    assert instance_shot.shot == shot
    assert instance_shot.parent.id == shot.id


def test_parent_sequence(instance_sequence, sequence):
    assert instance_sequence.sequence == sequence
    assert instance_sequence.parent.id == sequence.id


def test_parent_project(shot, project):
    assert shot.project == project


def test_find(instance_shot):
    assert instance_shot in Instance.find()


def test_findby_ids(instance_shot):
    assert instance_shot in Instance.findby_ids([instance_shot.id])


def test_find_one(instance_shot):
    assert instance_shot == Instance.find_one(id=instance_shot.id)


def test_findby_name(instance_shot):
    assert instance_shot == Instance.find_one(project=instance_shot.project,
                                              entity=instance_shot.shot,
                                              name=instance_shot.name)


def test_create_unique_shot_name(instance_shot):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        Instance.create(project=instance_shot.project, name=instance_shot.name,
                        asset=instance_shot.asset, entity=instance_shot.parent)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')


def test_create_unique_seq_name(instance_sequence):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        Instance.create(project=instance_sequence.project, name=instance_sequence.name,
                        asset=instance_sequence.asset, entity=instance_sequence.parent)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')


def test_create_bad_arguments_asset(instance_shot):
    # Expecting TypeError error, wrong argument/entity given.
    try:
        Instance.create(project=instance_shot.project, name=instance_shot.name,
                        asset=instance_shot.asset, entity=instance_shot.asset)
    except TypeError:
        return
    raise AssertionError('Expected TypeError due to wrong arg type')


def test_create_bad_arguments_shot(instance_shot):
    # Expecting TypeError error, wrong argument/entity given.
    try:
        Instance.create(project=instance_shot.project, name=instance_shot.name,
                        asset=instance_shot.shot, entity=instance_shot.shot)
    except TypeError:
        return
    raise AssertionError('Expected TypeError due to wrong arg type')
