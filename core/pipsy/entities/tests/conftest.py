import pytest
import sqlalchemy_utils.functions
from sqlalchemy.orm.exc import NoResultFound
import pipsy.db
from pipsy.db import connect_database, build_engine_url
from pipsy.entities.core import Base
from pipsy.entities import (Project, Episode, Sequence, Shot, Asset, Task, User)


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
    try:
        return Project.find_one(name='unittest', root='/tmp/unittest', schema='film')
    except NoResultFound:
        return Project.create(name='unittest', root='/tmp/unittest', schema='film')


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
        return Sequence.find_one(episode=episode, name='102')
    except NoResultFound:
        return Sequence.create(project=episode.project, episode=episode, name='102')


@pytest.fixture(scope="session")
def shot(sequence):
    try:
        return Shot.find_one(sequence=sequence, name='001')
    except NoResultFound:
        return Shot.create(project=sequence.project, sequence=sequence,
                           name='001', cut=(1001, 1002))


@pytest.fixture(scope="session")
def shot_episode(sequence_episode):
    try:
        return Shot.find_one(sequence=sequence_episode, name='001')
    except NoResultFound:
        return Shot.create(project=sequence_episode.project, sequence=sequence_episode,
                           name='001', cut=(1001, 1002))


@pytest.fixture(scope="session")
def asset(project):
    try:
        return Asset.find_one(project=project, name='cupcake', kind='prop')
    except NoResultFound:
        return Asset.create(project=project, name='cupcake', kind='prop')


@pytest.fixture(scope="session")
def task_shot(shot):
    try:
        return Task.find_one(project=shot.project, entity=shot,
                             name='anim pass', stage='animation')
    except NoResultFound:
        return Task.create(project=shot.project, entity=shot,
                           name='anim pass', stage='animation')


@pytest.fixture(scope="session")
def task_sequence(sequence):
    try:
        return Task.find_one(project=sequence.project, entity=sequence,
                             name='previs', stage='previs')
    except NoResultFound:
        return Task.create(project=sequence.project, entity=sequence,
                           name='previs', stage='previs')


@pytest.fixture(scope="session")
def task_asset(asset):
    try:
        return Task.find_one(project=asset.project, entity=asset,
                             name='build geo', stage='modeling')
    except NoResultFound:
        return Task.create(project=asset.project, entity=asset,
                           name='build geo', stage='modeling')


@pytest.fixture(scope="session")
def user(session, create_db):
    try:
        return User.find_one(first_name='unittest', last_name='unittest',
                             email='unittest@unittest.com', login='unittest')
    except NoResultFound:
        return User.create(first_name='unittest', last_name='unittest',
                           email='unittest@unittest.com', login='unittest')
