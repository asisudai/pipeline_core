import pytest
import sqlalchemy_utils.functions
from sqlalchemy.orm.exc import NoResultFound
import pipsy.db
from pipsy.db import connect_database, build_engine_url
from pipsy.entities.core import Base
from pipsy.entities import Project, Episode, Sequence, Shot


@pytest.fixture(scope="session")
def session(tmpdir_factory):
    pipsy.db.DATABASE = 'unittest'
    engine_url = build_engine_url(database='unittest')

    if not sqlalchemy_utils.functions.database_exists(engine_url):
        sqlalchemy_utils.functions.create_database(engine_url)
        # raise RuntimeError("Please create 'unittest' database for unittest.")

    session = connect_database(database='unittest')
    assert session.bind.url.database == 'unittest', "Not using 'unittest' database"

    return session


@pytest.fixture(scope="session")
def create_db(session):
    assert session.bind.url.database == 'unittest', "Not using 'unittest' database"
    Base.metadata.drop_all(session.connection().engine, checkfirst=True)
    Base.metadata.create_all(session.connection().engine, checkfirst=True)


@pytest.fixture(scope="session")
def project(session, create_db):
    new = Project.create(name='unittest', root='/tmp/unittest', schema='film')
    assert new in Project.find()
    return new


@pytest.fixture(scope="session")
def episode(project):
    try:
        return Episode.find_one(project=project, name='101')
    except NoResultFound:
        return Episode.create(project=project, name='101')


@pytest.fixture(scope="session")
def sequence(project):
    try:
        return Sequence.find_one(project=project, name='101')
    except NoResultFound:
        return Sequence.create(project=project, name='101')


@pytest.fixture(scope="session")
def sequence_episode(episode):
    try:
        return Sequence.find_one(episode=episode, name='101')
    except NoResultFound:
        return Sequence.create(project=episode.project, episode=episode, name='101')


@pytest.fixture(scope="session")
def shot(sequence):
    try:
        return Shot.find_one(sequence=sequence, name='001')
    except NoResultFound:
        return Shot.create(project=sequence.project, sequence=sequence, name='001')


@pytest.fixture(scope="session")
def shot_episode(sequence_episode):
    try:
        return Shot.find_one(sequence=sequence_episode, name='001')
    except NoResultFound:
        return Shot.create(project=sequence_episode.project, sequence=sequence_episode, name='001')
