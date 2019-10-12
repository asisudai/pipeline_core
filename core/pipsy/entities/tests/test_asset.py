from sqlalchemy.exc import IntegrityError
from pipsy.entities import Asset


def test_cls_name():
    assert Asset.cls_name() == 'Asset'


def test_project(asset, project):
    assert asset.project == project
    assert asset.project_id == project.id


def test_parent_project(asset, project):
    assert asset.parent == project


def test_find(asset):
    assert asset in Asset.find()


def test_findby_ids(asset):
    assert asset in Asset.findby_ids([asset.id])


def test_find_one(asset):
    assert asset == asset.find_one(id=asset.id)


def test_findby_name(asset):
    assert asset == Asset.find_one(project=asset.project,
                                   name=asset.name)


def test_create_unique_proj_name(asset):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        Asset.create(name=asset.name, project=asset.project, type=asset.type)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')
