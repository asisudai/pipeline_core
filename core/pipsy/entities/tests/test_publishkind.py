import pytest
from sqlalchemy.exc import IntegrityError
from pipsy.entities import PublishKind


@pytest.fixture(scope="module")
def kind_geohigh(create_publishkinds):
    return PublishKind.find_one(kind='geo', lod='high')


def test_cls_name():
    assert PublishKind.cls_name() == 'PublishKind'


def test_find(kind_geohigh):
    assert kind_geohigh in PublishKind.find()


def test_find_one(kind_geohigh):
    assert kind_geohigh == PublishKind.find_one(name=kind_geohigh.name,
                                                 lod=kind_geohigh.lod)


def test_findby_id(kind_geohigh):
    assert kind_geohigh == PublishKind.findby_id(kind_geohigh.id)


def test_findby_ids(kind_geohigh):
    assert kind_geohigh in PublishKind.findby_ids([kind_geohigh.id])


def test_findby_name(kind_geohigh):
    assert kind_geohigh == PublishKind.find_one(name=kind_geohigh.name)


def test_create_unique_name(kind_geohigh):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        PublishKind.create(name=kind_geohigh.name,
                           nicename=kind_geohigh.nicename + "_1",
                           kind=kind_geohigh.kind,
                           subkind=kind_geohigh.subkind,
                           lod=kind_geohigh.lod)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')


def test_create_unique_nicename(kind_geohigh):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        PublishKind.create(name=kind_geohigh.name + "_1",
                           nicename=kind_geohigh.nicename,
                           kind=kind_geohigh.kind,
                           subkind=kind_geohigh.subkind,
                           lod=kind_geohigh.lod)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')


def test_create_unique_kind_subkind_lod(kind_geohigh):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        PublishKind.create(name=kind_geohigh.name + "_2",
                           nicename=kind_geohigh.nicename + "_2",
                           kind=kind_geohigh.kind,
                           subkind=kind_geohigh.subkind,
                           lod=kind_geohigh.lod)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')
