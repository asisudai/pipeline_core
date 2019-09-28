import pytest
import sqlalchemy_utils.functions
from pipsy.db import connect_pipeline, build_engine_url
from pipsy.entities.core import Base
from pipsy.entities.project import Project


@pytest.fixture(scope="session")
def session(tmpdir_factory):
    engine_url = build_engine_url(database='unittest')

    if not sqlalchemy_utils.functions.database_exists(engine_url):
        raise RuntimeError("Please create 'unittest' database for unittest.")
        # sqlalchemy_utils.functions.create_database(engine_url)

    session = connect_pipeline(database='unittest')
    return session


@pytest.fixture(scope="session")
def create_db(session):
    Base.metadata.drop_all(session.connection().engine, checkfirst=True)
    Base.metadata.create_all(session.connection().engine, checkfirst=True)


@pytest.fixture(scope="session")
def project(session, create_db):
    new = Project.create(name='unittest', root='/tmp/unittest', session=session)
    assert new in Project.find()
    return new

