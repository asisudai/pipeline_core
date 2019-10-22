import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from pipsy.entities import PublishKind, PublishGroup, Publish


@pytest.fixture(scope="module")
def kind_geohigh(create_publishkinds):
    return PublishKind.find_one(kind='geo', lod='high')


@pytest.fixture(scope="module")
def shot_group(shot, kind_geohigh):
    try:
        return PublishGroup.find_one(project=shot.project, entity=shot, publishkind=kind_geohigh)
    except NoResultFound:
        return PublishGroup.create(project=shot.project, entity=shot, publishkind=kind_geohigh)


@pytest.fixture(scope="module")
def publish(shot_group, user):
    try:
        return Publish.find_one(project=shot_group.project, publishgroup=shot_group,
                                publishkind=shot_group.publishkind, user=user, version=1,
                                root='/tmp/path')
    except NoResultFound:
        return Publish.create(project=shot_group.project, publishgroup=shot_group,
                              publishkind=shot_group.publishkind, user=user, version=1,
                              root='/tmp/path')


def test_project(publish, project):
    assert publish.project == project


def test_publishkind(kind_geohigh, publish):
    assert publish.publishkind == kind_geohigh


def test_parent(publish, shot):
    assert publish.parent == shot


def test_publishgroup(publish, shot_group):
    assert publish.publishgroup == shot_group


def test_cls_name():
    assert Publish.cls_name() == 'Publish'


def test_find(publish):
    assert publish in Publish.find(project=publish.project)


def test_find_one(publish):
    assert publish == Publish.find_one(project=publish.project,
                                       publishgroup=publish.publishgroup,
                                       publishkind=publish.publishkind,
                                       version=publish.version,
                                       root=publish.root)


def test_findby_id(publish):
    assert publish == Publish.findby_id(publish.id)


def test_findby_ids(publish):
    assert publish in Publish.findby_ids([publish.id])


def test_create_unique_group_kind_version(publish):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        Publish.create(project=publish.project, publishgroup=publish.publishgroup,
                       publishkind=publish.publishkind, user=publish.user,
                       version=publish.version, root=publish.root + "_1")
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')


def test_create_unique_group_kind_root(publish):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        Publish.create(project=publish.project, publishgroup=publish.publishgroup,
                       publishkind=publish.publishkind, user=publish.user,
                       version=publish.version + 1, root=publish.root)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')
