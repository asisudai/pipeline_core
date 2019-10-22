import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from pipsy.entities import PublishKind, PublishGroup


@pytest.fixture(scope="module")
def kind_geohigh(create_publishkinds):
    return PublishKind.find_one(kind='geo', lod='high')


@pytest.fixture(scope="module")
def instance_group(instance, kind_geohigh):
    try:
        return PublishGroup.find_one(project=instance.project, entity=instance, publishkind=kind_geohigh)
    except NoResultFound:
        return PublishGroup.create(project=instance.project, entity=instance, publishkind=kind_geohigh)


@pytest.fixture(scope="module")
def shot_group(shot, kind_geohigh):
    try:
        return PublishGroup.find_one(project=shot.project, entity=shot, publishkind=kind_geohigh)
    except NoResultFound:
        return PublishGroup.create(project=shot.project, entity=shot, publishkind=kind_geohigh)


@pytest.fixture(scope="module")
def sequence_group(sequence, kind_geohigh):
    try:
        return PublishGroup.find_one(project=sequence.project, entity=sequence, publishkind=kind_geohigh)
    except NoResultFound:
        return PublishGroup.create(project=sequence.project, entity=sequence, publishkind=kind_geohigh)


def test_project(project, shot_group):
    assert shot_group.project == project


def test_kind(kind_geohigh, shot_group):
    assert shot_group.publishkind == kind_geohigh


def test_instance_parent(instance, instance_group):
    assert instance_group.parent == instance


def test_shot_parent(shot, shot_group):
    assert shot_group.parent == shot


def test_sequence_parent(sequence, sequence_group):
    assert sequence_group.parent == sequence


def test_cls_name():
    assert PublishGroup.cls_name() == 'PublishGroup'


def test_find(shot_group):
    assert shot_group in PublishGroup.find()


def test_find_one(shot_group):
    assert shot_group == PublishGroup.find_one(project=shot_group.project,
                                               entity=shot_group.parent,
                                               publishkind=shot_group.publishkind)


def test_findby_id(shot_group):
    assert shot_group == PublishGroup.findby_id(shot_group.id)


def test_findby_ids(shot_group):
    assert shot_group in PublishGroup.findby_ids([shot_group.id])


def test_create_unique_uq_sequence_kind(sequence_group):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        PublishGroup.create(project=sequence_group.project,
                            entity=sequence_group.parent,
                            publishkind=sequence_group.publishkind)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')


def test_create_unique_uq_shot_kind(shot_group):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        PublishGroup.create(project=shot_group.project,
                            entity=shot_group.parent,
                            publishkind=shot_group.publishkind)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')


def test_create_unique_uq_instance_kind(instance_group):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        PublishGroup.create(project=instance_group.project,
                            entity=instance_group.parent,
                            publishkind=instance_group.publishkind)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')
