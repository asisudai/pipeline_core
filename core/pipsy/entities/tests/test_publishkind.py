import pytest
from sqlalchemy.exc import IntegrityError
from pipsy.entities import PublishKind


@pytest.fixture(scope="module")
def kind_geo_high(create_publishkinds):
    return PublishKind.find_one(kind='geo', lod='high')


def test_cls_name():
    assert PublishKind.cls_name() == 'PublishKind'


def test_find(kind_geo_high):
    assert kind_geo_high in PublishKind.find()


def test_find_one(kind_geo_high):
    assert kind_geo_high == PublishKind.find_one(name=kind_geo_high.name,
                                                 lod=kind_geo_high.lod)


def test_findby_id(kind_geo_high):
    assert kind_geo_high == PublishKind.findby_id(kind_geo_high.id)


def test_findby_ids(kind_geo_high):
    assert kind_geo_high in PublishKind.findby_ids([kind_geo_high.id])


def test_findby_name(kind_geo_high):
    assert kind_geo_high == PublishKind.find_one(name=kind_geo_high.name)


def test_create_unique_name(kind_geo_high):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        PublishKind.create(name=kind_geo_high.name,
                           nicename=kind_geo_high.nicename + "_1",
                           kind=kind_geo_high.kind,
                           subkind=kind_geo_high.subkind,
                           lod=kind_geo_high.lod)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')


def test_create_unique_nicename(kind_geo_high):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        PublishKind.create(name=kind_geo_high.name + "_1",
                           nicename=kind_geo_high.nicename,
                           kind=kind_geo_high.kind,
                           subkind=kind_geo_high.subkind,
                           lod=kind_geo_high.lod)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')


def test_create_unique_kind_subkind_lod(kind_geo_high):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        PublishKind.create(name=kind_geo_high.name + "_2",
                           nicename=kind_geo_high.nicename + "_2",
                           kind=kind_geo_high.kind,
                           subkind=kind_geo_high.subkind,
                           lod=kind_geo_high.lod)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')
