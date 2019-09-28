from sqlalchemy.exc import IntegrityError
from pipsy.entities.project import Project


def test_find(project):
    assert project in Project.find()


def test_findby_ids(project):
    assert project in Project.findby_ids([project.id])


def test_findby_name(project):
    assert project == Project.findby_name(project.name)


def test_find_one(project):
    assert project == Project.find_one(name=project.name)


def test_create_unique_name(project, session):
    try:
        # Expecting IntegrityError error "Duplicate entry..."
        Project.create(name='unittest', root='/tmp/unittest2', session=session)
        raise AssertionError('Duplicate entry for project name was NOT cought!')
    except IntegrityError:
        pass


def test_create_unique_root(project, session):
    try:
        # Expecting IntegrityError error "Duplicate entry..."
        Project.create(name='unittest2', root='/tmp/unittest', session=session)
        raise AssertionError('Duplicate entry for project root was NOT cought!')
    except IntegrityError:
        pass
