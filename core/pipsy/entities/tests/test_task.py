from sqlalchemy.exc import IntegrityError
from pipsy.entities import Task


def test_cls_name():
    assert Task.cls_name() == 'Task'


def test_project(task_asset, project):
    assert task_asset.project == project
    assert task_asset.project_id == project.id


def test_parent_sequence(task_sequence, project):
    assert task_sequence.parent == task_sequence.sequence


def test_parent_shot(task_shot, project):
    assert task_shot.parent == task_shot.shot


def test_parent_asset(task_asset, project):
    assert task_asset.parent == task_asset.asset


def test_find(task_asset):
    assert task_asset in Task.find()


def test_findby_ids(task_asset):
    assert task_asset in Task.findby_ids([task_asset.id])


def test_find_one(task_asset):
    assert task_asset == task_asset.find_one(id=task_asset.id)


def test_findby_name(task_asset):
    assert task_asset == Task.find_one(project=task_asset.project,
                                       name=task_asset.name)


def test_create_unique_proj_name(task_asset):
    # Expecting IntegrityError error "Duplicate entry..."
    try:
        Task.create(project=task_asset.project, entity=task_asset.parent,
                    name=task_asset.name, stage=task_asset.stage)
    except IntegrityError:
        return
    raise AssertionError('Expected IntegrityError due to "Duplicate entry"')
