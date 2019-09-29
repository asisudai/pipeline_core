import pytest
from sqlalchemy.orm.exc import NoResultFound
from pipsy.entities import Preset


@pytest.fixture(scope="module")
def preset(project):
    try:
        return Preset.find_one(entity=project)
    except NoResultFound:
        return Preset.create(entity=project)


def test_cls_name():
    assert Preset.cls_name() == 'Preset'


def test_preset(preset, project):
    assert preset.project_id == project.id
    assert preset.project == project


def test_find(preset):
    assert preset in preset.find()


def test_findby_ids(preset):
    assert preset in preset.findby_ids([preset.id])


def test_find_one(preset):
    assert preset == preset.find_one(name=preset.name)
