from sqlalchemy.exc import IntegrityError
from pipsy.entities.core import BaseEntity, EntityTypeError


def test_cls_name():
    assert BaseEntity.cls_name() == 'BaseEntity'


def test_project_eq(project):
    assert project == project


def test_project_default_status(project):
    assert project.default_status()


def test_project_disabled_statuses(project):
    assert isinstance(project.disabled_statuses(), (list, tuple))


def test_project_is_active(project):
    assert project.is_active() is True


def test_project_is_disabled(project):
    assert project.is_disabled() is False


def test_assert_isinstance(project, episode, sequence, shot, asset):
    BaseEntity.assert_isinstance(project, 'Project')
    BaseEntity.assert_isinstance(episode, 'Episode')
    BaseEntity.assert_isinstance(sequence, 'Sequence')
    BaseEntity.assert_isinstance(shot, 'Shot')
    BaseEntity.assert_isinstance(asset, 'Asset')


def test_assert_isinstance_entitytypeerror(project):
    try:
        BaseEntity.assert_isinstance(project, 'Shot')
    except EntityTypeError:
        return
    raise AssertionError('Expected EntityTypeError due to invalid instance')


def test_assert_isinstances(project, episode, sequence, shot, asset):
    BaseEntity.assert_isinstances([project], 'Project')
    BaseEntity.assert_isinstances([episode], 'Episode')
    BaseEntity.assert_isinstances([sequence], 'Sequence')
    BaseEntity.assert_isinstances([shot], 'Shot')
    BaseEntity.assert_isinstances([asset], 'Asset')


def test_assert_isinstances_entitytypeerror(project):
    try:
        BaseEntity.assert_isinstance([project], 'Shot')
    except EntityTypeError:
        return
    raise AssertionError('Expected EntityTypeError due to invalid instance')
