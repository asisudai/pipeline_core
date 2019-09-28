from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.pool import NullPool
from .. core import logging
from .. config import config

LOG = logging.getLogger(__name__, level=logging.INFO)

# configuration
RDBMS    = config.get('database', 'rdbms')
HOST     = config.get('database', 'host')
PORT     = config.get('database', 'port')
DATABASE = config.get('database', 'database')
USER     = config.get('database', 'user')
PASSWD   = config.get('database', 'passwd')

__cached_sessions = {}


def connect_database(rdbms=RDBMS, host=HOST, port=PORT, user=USER,
                     password=PASSWD, database=DATABASE):
    '''
    Create a session connection to database.

        Args:
            rdbms    (str) : Relational Database Management System e.g. [mysql, sqlite]
            host     (str) : hostname or IP
            port     (str) : port to access.
            user     (str) : authorized username.
            password (str) : user's password.
            database (str) : database to select.

        Returns:
            Session instance.
    '''
    engine_url = build_engine_url(rdbms, host, port, user, password, database)

    if not __cached_sessions.get(engine_url):
        __cached_sessions[engine_url] = __make_session(engine_url)

    return __cached_sessions[engine_url]


def build_engine_url(rdbms=RDBMS, host=HOST, port=PORT, user=USER, password=PASSWD,
                     database=DATABASE):
    '''
    Create engine_url to be used when calling create_engine()

        Args:
            rdbms    (str) : Relational Database Management System e.g. [mysql, sqlite]
            host     (str) : hostname or IP
            port     (str) : port to access.
            user     (str) : authorized username.
            password (str) : user's password.
            database (str) : database to select.

        Returns:
            engine url string.    
    '''
    params = ''
    if rdbms == 'mysql':
        params = 'sql_mode=STRICT_ALL_TABLES'

    url = '{rdbms}://{user}:{password}@{host}:{port}/{database}?{params}'.format(
          rdbms=rdbms, user=user, password=password, host=host, port=port, database=database,
          params=params)
    return url

@contextmanager
def session_context():
    '''
    Provide a transactional scope around a series of operations.

        e.g.
        with session_context() as session:
            session.add()
    '''
    session = connect_database(rdbms=RDBMS, host=HOST, port=PORT, user=USER,
                               password=PASSWD, database=DATABASE)
    session.begin(subtransactions=True)

    try:
        yield session
        session.commit()
    except (DataError, IntegrityError) as err:
        LOG.fatal('{} {}'.format(err.__class__.__name__, err))
        LOG.fatal('{} {}'.format(err.statement, err.params))
        session.rollback()
        raise
    except Exception:
        session.rollback()
        raise


def __make_session(engine_url):
    """
    Create a new scoped session.

    Args:
        engine_url (str): a valid MySQL DBAPIs string.
                             "mysql://user:password@%:3306/database"
    """
    engine = create_engine(engine_url, poolclass=NullPool, echo=False, encoding="utf-8")
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=True)
    scoped_session_ = scoped_session(session_factory)
    return scoped_session_

