import pytest
from sqlalchemy.exc import DataError, IntegrityError
from pipsy.db import connect_pipeline
from pipsy.entities.core import Base
from pipsy.entities.project import Project


@pytest.fixture(scope="module")
def session(tmpdir_factory):
    session = connect_pipeline()
    return session


@pytest.fixture(scope="module")
def create_db(session):
    Base.metadata.drop_all(session.connection().engine, checkfirst=True)
    Base.metadata.create_all(session.connection().engine, checkfirst=True)


def test_project(session, create_db, capsys):
    # with capsys.disabled():
    new = Project.create(name='unittest', root='/tmp/unittest')
    assert new in Project.find()
    # print(Project.find())
    
    # Catch unique constraint "Duplicate entry..."
    try:
        Project.create(name='unittest', root='/tmp/unittest')
    except Exception, err:
        assert isinstance(err, IntegrityError)
