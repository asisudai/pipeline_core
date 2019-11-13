import pytest
from pipsy.schema import core


@pytest.fixture('module')
def schema_film():
    schema = core.read_schema('film')
    assert isinstance(schema, dict)
    return schema


def test_expand_values_task_shot(task_shot):
    result = core._expand_fields({task_shot.cls_name(): task_shot, 'key': 'value'})
    assert task_shot.project in result.values()
    assert task_shot.shot in result.values()
    assert 'key' in result
    assert 'value' in result.values()


def test_expand_values_task_asset(task_asset):
    result = core._expand_fields({task_asset.cls_name(): task_asset, 'key': 'value'})
    assert task_asset.project in result.values()
    assert task_asset.asset in result.values()
    assert 'key' in result
    assert 'value' in result.values()


def test_film_get_raw_path():
    assert core.get_raw_path('project_root', 'film')
    assert core.get_raw_path('asset_root', 'film')
    assert core.get_raw_path('sequence_root', 'film')
    assert core.get_raw_path('shot_root', 'film')


def test_get_raw_path_fields():
    assert core.get_raw_path_fields('project_root', 'film') == ['project']
    assert core.get_raw_path_fields('asset_root', 'film') == ['project', 'asset']
    assert core.get_raw_path_fields('sequence_root', 'film') == ['project', 'sequence']
    assert core.get_raw_path_fields('shot_root', 'film') == ['project', 'sequence', 'shot']


def test_get_path_shot_film(shot):
    fields = {'shot': shot}
    assert core.get_path('project_root', fields, 'film') == '/tmp/unittest'
    assert core.get_path('shot_root', fields, 'film') == '/tmp/unittest/sequence/101/001'
    assert core.get_path('shot_pub', fields, 'film') == '/tmp/unittest/sequence/101/001/pub'


# def test_get_path_keyerror(capsys):
#     # TODO: expect it to fail on KeyError
#     # with capsys.disabled():
#     raise NotImplemented()
