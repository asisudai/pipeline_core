from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import DataError, IntegrityError, InvalidRequestError
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


def connect_pipeline(rdbms=RDBMS, host=HOST, port=PORT, user=USER,
                     password=PASSWD, database=DATABASE):
    '''
    The main connect function to our pipeline database

    Args:
        rdbms    (str) :
        host     (str) :
        port     (str) :
        user     (str) :
        password (str) :
        db       (str) :
    '''
    engine_url = build_engine_url(rdbms, host, port, user, password, database)

    if not __cached_sessions.get(engine_url):
        __cached_sessions[engine_url] = __make_session(engine_url)

    return __cached_sessions[engine_url]


def build_engine_url(rdbms=RDBMS, host=HOST, port=PORT, user=USER, password=PASSWD,
                     database=DATABASE):
    '''
    Build engine_url to be used when calling create_engine()
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
    session = connect_pipeline()
    session.begin(subtransactions=True)
    try:
        yield session
    except (DataError, IntegrityError) as err:
        LOG.fatal('{} {}'.format(err.__class__.__name__, err.message))
        LOG.fatal('{} {}'.format(err.statement, err.params))
        if session:
            session.rollback()
        raise
    except Exception:
        if session.transaction or session.transaction.is_active:
            session.rollback()
        raise
    else:
        session.commit()


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




# class Connection(object):
#     '''
#     Wrapper class over the session object.
#     '''

#     def __init__(self, engine_str):
#         """
#         Create a new database session.

#         Args:
#             engine_str (str): a valid MySQL DBAPIs string.
#                               "mysql://user:password@%:3306/pipeline"
#         """
#         self.engine_str = engine_str
#         self.engine = create_engine(self.engine_str, poolclass=NullPool,
#                                     echo=False, encoding="utf-8")
#         self._session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=True)
#         self._scoped_session = scoped_session(self._session_factory)


#     def __getattr__(self, name):
#         """
#         Handles the case when an attribute or method not in DBConnection is accessed.
#         Attempt to grab the same attribute/method in the child Session instead.
#         """
#         return getattr(self.session, name)

#     @property
#     def session(self):
#         """
#         Returns an open session for this connection.
#         """
#         session = self._scoped_session()
#         return session

#     @contextmanager
#     def session_context(self):
#         """Provide a transactional scope around a series of operations."""
#         self.session.begin(subtransactions=True)
#         try:
#             yield self.session
#         except Exception:
#             if self.session.transaction or self.session.transaction.is_active:
#                 self.session.rollback()
#             raise
#         else:
#             self.session.commit()

#     def query(self, *args):
#         """
#         Query
#         """
#         session = self._scoped_session()

#         # If we're not in a transaction, we want fresh stuff in our identity map.
#         if not self.session.transaction or not self.session.transaction.is_active:
#             return session.query(*args).populate_existing()

#         return session.query(*args)

#     def start_transaction(self):
#         """
#         Start keeping our transaction open over multiple calls to get_session.
#         """
#         # Subtransactions=True is required b/c autocommit is on.
#         self.session.begin(subtransactions=True)

#     def commit_transaction(self):
#         """
#         Commit the data in the current transaction.
#         """
#         self.session.commit()

#     def rollback_transaction(self):
#         """
#         Rollback the data in the current transaction.
#         """
#         if self.session.transaction:
#             self.session.rollback()
