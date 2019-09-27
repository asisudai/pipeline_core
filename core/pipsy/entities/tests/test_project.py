import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session as scoped_session_
from sqlalchemy.orm import scoped_session
from sqlalchemy.pool import NullPool
from pipsy.entities.core import Base
from pipsy.entities.project import Project


@pytest.fixture(scope="module")
def session(tmpdir_factory):
    sqlite_db = tmpdir_factory.mktemp('pytest').join('pytest.sqlite')
    engine = create_engine('sqlite:///{}'.format(sqlite_db.strpath),
                           poolclass=NullPool, echo=False, encoding="utf-8")
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=True)
    scoped_session = scoped_session_(session_factory)
    return scoped_session


@pytest.fixture(scope="module")
def create_db(session):
    Base.metadata.drop_all(session.connection().engine, checkfirst=True)
    Base.metadata.create_all(session.connection().engine, checkfirst=True)


def test_project(session, create_db, capsys):
    with capsys.disabled():
        new = Project(name='test', root='/tmp/project')
        session.begin(subtransactions=True)
        session.add(new)
        session.commit()

        print(Project.find())
