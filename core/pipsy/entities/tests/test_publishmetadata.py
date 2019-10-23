import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from pipsy.entities import PublishKind, PublishGroup, Publish, PublishMetadata


@pytest.fixture(scope="module")
def publish(publishgroup_shot, user):
    try:
        return Publish.find_one(project=publishgroup_shot.project, publishgroup=publishgroup_shot,
                                publishkind=publishgroup_shot.publishkind, user=user, version=1,
                                root='/tmp/path')
    except NoResultFound:
        return Publish.create(project=publishgroup_shot.project, publishgroup=publishgroup_shot,
                              publishkind=publishgroup_shot.publishkind, user=user, version=1,
                              root='/tmp/path')

def test_cls_name():
    assert PublishMetadata.cls_name() == 'PublishMetadata'


@pytest.fixture(scope="module")
def publish_metadata(publish):
    try:
        return PublishMetadata.find_one(publish=publish)
    except NoResultFound:
        return PublishMetadata.create(publish=publish,
                                      metadata={'key': 'value'})


def test_publish_get_metadata(publish_metadata, publish):
    assert publish.metadata == publish_metadata.metadata


def test_publish_set_metadata(publish_metadata, publish):
    data = publish.metadata.copy()
    data.update({'new_key': 'new_value'})
    publish.metadata = data
    assert 'new_key' in publish_metadata.metadata.keys()


def test_metadata(publish_metadata):
    assert publish_metadata.metadata


def test_has_key(publish_metadata):
    assert publish_metadata in PublishMetadata.find(
        has_key=publish_metadata.metadata.keys()[0])


def test_has_key(publish_metadata):
    key = publish_metadata.metadata.keys()[0]
    value = publish_metadata.metadata[key]
    assert publish_metadata in PublishMetadata.find(key_value=(key, value))
