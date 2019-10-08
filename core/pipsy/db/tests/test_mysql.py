import pytest
from pipsy import db


@pytest.fixture(scope="module")
def session():
    session = db.connect_database()
    return session


def test_connect_pipeline(session):
    '''Connect to pipeline's database'''
    databases = session.bind.execute('show databases;').fetchall()
    assert ((db.DATABASE,) in databases), 'expected {!r} to be in databases'.format(db.DATABASE)
