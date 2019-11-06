import pytest
from pipsy.schema import core

@pytest.fixture('module')
def schema_film():
    schema = core.read_schema('film')
    assert isinstance(schema, dict)
    return schema


def test_expand_values_task_shot(task_shot):
    result = core._expand_values({task_shot.cls_name(): task_shot, 'key': 'value'})
    assert task_shot.project in result.values()
    assert task_shot.shot in result.values()
    assert 'key' in result
    assert 'value' in result.values()


def test_expand_values_task_asset(task_asset):
    result = core._expand_values({task_asset.cls_name(): task_asset, 'key': 'value'})
    assert task_asset.project in result.values()
    assert task_asset.asset in result.values()
    assert 'key' in result
    assert 'value' in result.values()


# def test_iter_schema_film_task_asset(task_asset, capsys):
#     values = {task_asset.cls_name(): task_asset}

#     with capsys.disabled():
#         for item in core.iter_schema('film', values):
#             print(item)
