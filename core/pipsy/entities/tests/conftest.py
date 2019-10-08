import pytest
import sqlalchemy_utils.functions
import pipsy.db
from pipsy.db import connect_database, build_engine_url
from pipsy.entities.core import Base
from pipsy.entities.project import Project


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

    # Generated column for episode_id_virtual to support unique constraint with NULL episodes
    session.bind.execute("ALTER TABLE `unittest`.`sequence` CHANGE COLUMN `episode_id_virtual` `episode_id_virtual` INT(11) GENERATED ALWAYS AS(IFNULL(`episode_id`, 0)) STORED")


@pytest.fixture(scope="session")
def project(session, create_db):
    new = Project.create(name='unittest', root='/tmp/unittest', schema='film')
    assert new in Project.find()
    return new
