#!/usr/bin/env python
'''Entities Base Class'''

# imports
from contextlib import contextmanager
from sqlalchemy import inspect, MetaData, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.util import identity_key
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import DataError, IntegrityError
from .. import db
from ..core.pythonx import int, string_types
from ..core import logging

LOG = logging.getLogger(__name__, level=logging.INFO)


class BaseEntity(object):
    '''SCL entities base class'''

    def __init__(self, **columns):
        self._columns = columns

        for key, value in columns.iteritems():
            setattr(self, key, value)

    def __repr__(self):
        return "{cls}(name='{name}', id={id})".format(cls=self.__class__.__name__,
                                                      name=self.name,
                                                      id=self.id)

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and \
               (identity_key(instance=self) == identity_key(instance=other))

    def __hash__(self):
        key = identity_key(instance=self)
        if len(key) == 1:
            key = key[0]

        return hash((self.__class__, key))

    def __iter__(self):
        def convert_datetime(value):
            if value:
                return value.strftime("%Y-%m-%d %H:%M:%S")

        for col in self.__table__.columns:
            if isinstance(col.type, DateTime):
                value = convert_datetime(getattr(self, col.name))
            else:
                value = getattr(self, col.name)

            yield(col.name, value)

    @classmethod
    def default_status(cls):
        '''Return string of the default status'''
        column = cls.__table__.columns.get('status')
        return column.default.arg

    @classmethod
    def disabled_statuses(cls):
        '''Return a tuple of disabled statuses'''
        return ('dis',)

    def is_disabled(self):
        '''Return True/False if disabled'''
        return (self.status in self.disabled_statuses())

    def is_active(self):
        '''Return True/False if active'''
        return (self.status not in self.disabled_statuses())

    @contextmanager
    def session_context(self):
        '''Return a entity's session context'''
        session = inspect(self).session
        assert session, '{} is not attached to any session'.format(self)
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

    @classmethod
    def find(cls, **kwargs):
        '''find() must be override by subclass'''
        raise NotImplementedError(
            'find() must be implemented by subclass "{}"'.format(cls.__name__))

    @classmethod
    def find_one(cls, **kwargs):
        '''
        Wrapper of find() that return a single result.
        Will error if None or more then one results found.
        '''
        result = cls.find(**kwargs)

        if not result:
            raise NoResultFound(
                "No {} found for query:{}".format(cls.__name__, kwargs))
        elif len(result) > 1:
            raise MultipleResultsFound(
                "More than one {} found for query:{}".format(cls.__name__, kwargs))
        else:
            return result[0]

    @classmethod
    def findby_id(cls, id):
        '''Return an instance based on given id
        Will error out if no result found.

        args:
            id (int): The id to search by.
        '''
        try:
            return cls.query().filter_by(id=id).one()
        except NoResultFound:
            raise NoResultFound(
                "No {} found for id:{}".format(cls.__name__, id))

    @classmethod
    def findby_ids(cls, ids):
        '''Return instances based on given ids.
        Will return an empty list if none found.

        args:
            ids (list): The ids to search by.
        '''
        return cls.query().filter(cls.id.in_(ids)).all()

    @classmethod
    def create(cls, **kw):
        '''
        Create a new entity in the database.
        Will do SQL insert call to the db, making this entity permanently available.
        '''
        with db.session_context() as session:
            new = cls(**kw)
            session.add(new)
        return new

    @classmethod
    def cls_name(cls):
        '''Returns entity's class name'''
        return cls.__name__

    @classmethod
    def query(cls, project=None, name=None, id=None, status=None, shotgun_id=None):
        '''
        Return a Query instance. Supports common queries done by entities.
        '''
        query = cls.__connect().query(cls)

        if project:
            cls.assert_isinstance(project, 'Project')
            query = query.filter(cls.project_id == project.id)

        if name:
            query = query.filter(cls.name == name)

        if id:
            if isinstance(id, int):
                query = query.filter(cls.id == id)
            elif isinstance(id, (list, tuple)):
                query = query.filter(cls.id.in_(id))
            else:
                raise ValueError('Invalid argument given {}'.format(type(id)))

        if status:
            if isinstance(status, (list, tuple)):
                query = query.filter(cls.status.in_(status))
            elif isinstance(status, string_types):
                query = query.filter(cls.status == status)
            else:
                raise ValueError('Invalid argument given {}'.format(id))

        if shotgun_id:
            if isinstance(shotgun_id, int):
                query = query.filter(cls.shotgun_id == shotgun_id)
            elif isinstance(shotgun_id, (list, tuple)):
                query = query.filter(cls.shotgun_id.in_(shotgun_id))
            else:
                raise ValueError('Invalid argument given {}'.format(type(shotgun_id)))

        return query

    @classmethod
    def __connect(cls):
        '''
        Returns db connection.
        Better to use self.session_context with instance.
        '''
        return db.connect_database(rdbms=db.RDBMS, host=db.HOST, port=db.PORT, user=db.USER,
                                   password=db.PASSWD, database=db.DATABASE)

    @staticmethod
    def assert_isinstances(entities, expected_cls):
        '''Helper assertion to validate given object is expected list of Entity class'''
        expected_cls = [expected_cls] if isinstance(expected_cls, string_types) else expected_cls
        for entity in entities:
            if not isinstance(entity, Base) or not entity.cls_name() in expected_cls:
                raise EntityTypeError('Expected {!r} entity. Given {!r}'
                                      .format(expected_cls, type(entity)))

    @staticmethod
    def assert_isinstance(entity, expected_cls):
        '''Helper assertion to validate given object is expected Entity class'''
        expected_cls = [expected_cls] if isinstance(expected_cls, string_types) else expected_cls
        if not isinstance(entity, Base) or not entity.cls_name() in expected_cls:
            raise EntityTypeError('Expected {!r} entity. Given {!r}'
                                  .format(expected_cls, type(entity)))


# Register BaseEntity with sqlAlchemy declarative base.
metadata = MetaData()
Base = declarative_base(cls=BaseEntity, metadata=metadata)


class AttributeDict(dict):
    '''Python magic. magic.'''
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class ResultSet(set):
    '''
    Set with extended support for operators.
        s = ResultSet()
        s = []
        s += 1
        s -= [1]
        s == [3]
        s != [4]
    '''
    def __iadd__(self, other):
        if isinstance(other, list):
            self.update(other)
        else:
            self.add(other)
        return self

    def __isub__(self, other):
        if isinstance(other, list):
            self.difference_update(other)
        else:
            self.discard(other)
        return self

    def __eq__(self, other):
        if isinstance(other, list):
            return list(self) == other
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class EntityTypeError(TypeError):
    pass
